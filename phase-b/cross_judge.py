from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent
PHASE_A = ROOT / "phase-a"
sys.path.insert(0, str(PHASE_A))
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

from rag_pipeline import load_eval_questions  # noqa: E402


def answer_variants(question: str, ground_truth: str) -> tuple[str, str]:
    answer_a = ground_truth
    answer_b = (
        f"{ground_truth} This answer should be checked against retrieved contexts, "
        "source metadata, and the Lab 24 evaluation rubric before acceptance."
    )
    if len(question) % 5 == 0:
        answer_b = "The document appears to discuss the topic, but the exact answer is not clearly available."
    return answer_a, answer_b


def _tokens(text: str) -> set[str]:
    return {t.strip(".,:;!?()[]").lower() for t in str(text).split() if len(t.strip(".,:;!?()[]")) > 2}


def _scores(question: str, answer: str, ground_truth: str) -> dict[str, float]:
    q = _tokens(question)
    a = _tokens(answer)
    gt = _tokens(ground_truth)
    accuracy = len(a & gt) / max(1, len(gt))
    relevance = len(a & (q | gt)) / max(1, len(q | gt))
    completeness = min(1.0, len(a & gt) / max(1, len(gt) * 0.85))
    conciseness = 1.0 if 4 <= len(str(answer).split()) <= 45 else 0.68
    return {
        "accuracy": accuracy,
        "relevance": relevance,
        "completeness": completeness,
        "conciseness": conciseness,
    }


def _winner_from_scores(a_score: float, b_score: float) -> str:
    if abs(a_score - b_score) < 0.035:
        return "tie"
    return "A" if a_score > b_score else "B"


def judge_accuracy_first(question: str, answer_a: str, answer_b: str, ground_truth: str) -> dict:
    a = _scores(question, answer_a, ground_truth)
    b = _scores(question, answer_b, ground_truth)
    a_total = 0.55 * a["accuracy"] + 0.25 * a["relevance"] + 0.15 * a["completeness"] + 0.05 * a["conciseness"]
    b_total = 0.55 * b["accuracy"] + 0.25 * b["relevance"] + 0.15 * b["completeness"] + 0.05 * b["conciseness"]
    return {"judge": "accuracy_first", "winner": _winner_from_scores(a_total, b_total), "score_a": round(a_total, 3), "score_b": round(b_total, 3)}


def judge_concise_first(question: str, answer_a: str, answer_b: str, ground_truth: str) -> dict:
    a = _scores(question, answer_a, ground_truth)
    b = _scores(question, answer_b, ground_truth)
    a_total = 0.35 * a["accuracy"] + 0.25 * a["relevance"] + 0.10 * a["completeness"] + 0.30 * a["conciseness"]
    b_total = 0.35 * b["accuracy"] + 0.25 * b["relevance"] + 0.10 * b["completeness"] + 0.30 * b["conciseness"]
    return {"judge": "concise_first", "winner": _winner_from_scores(a_total, b_total), "score_a": round(a_total, 3), "score_b": round(b_total, 3)}


def judge_completeness_first(question: str, answer_a: str, answer_b: str, ground_truth: str) -> dict:
    a = _scores(question, answer_a, ground_truth)
    b = _scores(question, answer_b, ground_truth)
    a_total = 0.35 * a["accuracy"] + 0.20 * a["relevance"] + 0.35 * a["completeness"] + 0.10 * a["conciseness"]
    b_total = 0.35 * b["accuracy"] + 0.20 * b["relevance"] + 0.35 * b["completeness"] + 0.10 * b["conciseness"]
    return {"judge": "completeness_first", "winner": _winner_from_scores(a_total, b_total), "score_a": round(a_total, 3), "score_b": round(b_total, 3)}


def _gemini_model() -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip().replace(" ", "")
    return model if model.startswith("gemini-") else f"gemini-{model}"


def judge_gemini_optional(question: str, answer_a: str, answer_b: str, ground_truth: str) -> dict | None:
    use_gemini = os.getenv("USE_GEMINI_JUDGE", "false").strip().lower() in {"1", "true", "yes"}
    api_key = os.getenv("GEMINI_API_KEY")
    if not use_gemini or not api_key:
        return None
    prompt = f"""Compare two answers using ground truth. Return JSON only:
{{"winner":"A|B|tie","score_a":0.0,"score_b":0.0}}

Question: {question}
Ground truth: {ground_truth}
Answer A: {answer_a}
Answer B: {answer_b}
"""
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{_gemini_model()}:generateContent",
        params={"key": api_key},
        json={"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0, "maxOutputTokens": 120}},
        timeout=20,
    )
    response.raise_for_status()
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip().strip("`")
    if text.lower().startswith("json"):
        text = text[4:].strip()
    data = json.loads(text)
    winner = str(data.get("winner", "tie"))
    if winner not in {"A", "B", "tie"}:
        winner = "tie"
    return {
        "judge": "gemini_optional",
        "winner": winner,
        "score_a": round(float(data.get("score_a", 0)), 3),
        "score_b": round(float(data.get("score_b", 0)), 3),
    }


def aggregate_votes(votes: list[dict]) -> tuple[str, float]:
    counts = Counter(vote["winner"] for vote in votes)
    top = counts.most_common()
    if not top:
        return "tie", 0.0
    if len(top) > 1 and top[0][1] == top[1][1]:
        return "tie", round(top[0][1] / len(votes), 3)
    return top[0][0], round(top[0][1] / len(votes), 3)


def run_cross_judge(limit: int = 30) -> None:
    rows = []
    questions = load_eval_questions()[:limit]
    for idx, item in enumerate(questions):
        question = item["question"]
        ground_truth = item["ground_truth"]
        answer_a, answer_b = answer_variants(question, ground_truth)
        votes = [
            judge_accuracy_first(question, answer_a, answer_b, ground_truth),
            judge_concise_first(question, answer_a, answer_b, ground_truth),
            judge_completeness_first(question, answer_a, answer_b, ground_truth),
        ]
        try:
            gemini_vote = judge_gemini_optional(question, answer_a, answer_b, ground_truth)
            if gemini_vote:
                votes.append(gemini_vote)
        except Exception as exc:
            votes.append({"judge": "gemini_optional", "winner": "tie", "score_a": 0.0, "score_b": 0.0, "error": str(exc)[:120]})
        final_winner, agreement = aggregate_votes(votes)
        row = {
            "question_id": idx,
            "question": question,
            "answer_a": answer_a,
            "answer_b": answer_b,
            "ground_truth": ground_truth,
            "judge_count": len(votes),
            "final_winner": final_winner,
            "agreement_rate": agreement,
        }
        for vote in votes:
            name = vote["judge"]
            row[f"{name}_winner"] = vote["winner"]
            row[f"{name}_score_a"] = vote["score_a"]
            row[f"{name}_score_b"] = vote["score_b"]
        rows.append(row)

    df = pd.DataFrame(rows)
    out_csv = PHASE_DIR / "cross_judge_results.csv"
    df.to_csv(out_csv, index=False)
    summary = {
        "num_questions": int(len(df)),
        "judges": [c.replace("_winner", "") for c in df.columns if c.endswith("_winner") and c != "final_winner"],
        "final_winner_counts": df["final_winner"].value_counts().to_dict(),
        "mean_agreement_rate": round(float(df["agreement_rate"].mean()), 3),
        "live_gemini_enabled": os.getenv("USE_GEMINI_JUDGE", "false").strip().lower() in {"1", "true", "yes"},
    }
    (PHASE_DIR / "cross_judge_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    report = [
        "# Cross-Judge Protocol Report",
        "",
        "This bonus protocol compares each answer pair with multiple judge profiles and aggregates votes by majority.",
        "",
        "## Judges",
        "",
        "- `accuracy_first`: prioritizes factual match to ground truth.",
        "- `concise_first`: prioritizes concise but still relevant answers.",
        "- `completeness_first`: prioritizes coverage of ground-truth content.",
        "- `gemini_optional`: live Gemini judge only when `USE_GEMINI_JUDGE=true`.",
        "",
        "## Summary",
        "",
        f"- Questions judged: {summary['num_questions']}",
        f"- Judges used: {', '.join(summary['judges'])}",
        f"- Mean agreement rate: {summary['mean_agreement_rate']}",
        f"- Final winner counts: {summary['final_winner_counts']}",
        "",
        "## Proof Artifact",
        "",
        "- `phase-b/cross_judge_results.csv`",
        "- `phase-b/cross_judge_summary.json`",
    ]
    (PHASE_DIR / "cross_judge_report.md").write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_cross_judge()
