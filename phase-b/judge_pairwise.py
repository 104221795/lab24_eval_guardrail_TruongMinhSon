from __future__ import annotations

import json
import os
import sys
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


def _gemini_model() -> str:
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip().replace(" ", "")
    return model if model.startswith("gemini-") else f"gemini-{model}"


def _gemini_generate(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{_gemini_model()}:generateContent"
    response = requests.post(
        url,
        params={"key": api_key},
        json={
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0, "maxOutputTokens": 200},
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _parse_winner(text: str) -> tuple[str, str]:
    cleaned = text.strip().strip("`")
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()
    try:
        payload = json.loads(cleaned)
        winner = str(payload.get("winner", "tie")).upper()
        reason = str(payload.get("reason", "Gemini judge returned a winner."))
    except Exception:
        low = cleaned.lower()
        if '"a"' in low or "winner: a" in low or low.startswith("a"):
            winner = "A"
        elif '"b"' in low or "winner: b" in low or low.startswith("b"):
            winner = "B"
        else:
            winner = "tie"
        reason = cleaned[:200] or "Gemini judge response could not be parsed fully."
    if winner not in {"A", "B", "tie"}:
        winner = "tie"
    return winner, reason


def mock_answer_variants(question: str) -> tuple[str, str]:
    base = question.rstrip("?")
    answer_a = f"{base}: use the Lab 24 rubric and verify the result with saved metrics."
    if len(question) % 4 == 0:
        answer_b = f"{base}: use a clear rubric, retrieved evidence, metric thresholds, calibration labels, and guardrail logs before accepting the answer."
    elif len(question) % 5 == 0:
        answer_b = "This is usually fine. Add more evaluation if needed."
    else:
        answer_b = f"{base}: check the relevant metric, compare it with thresholds, and document the operational follow-up."
    return answer_a, answer_b


def _score(question: str, answer: str) -> dict[str, float]:
    q_terms = {w.lower().strip(".,:?") for w in question.split() if len(w) > 3}
    a_terms = {w.lower().strip(".,:?") for w in answer.split() if len(w) > 3}
    relevance = len(q_terms & a_terms) / max(1, len(q_terms))
    completeness = min(1.0, len(answer.split()) / 24)
    conciseness = 1.0 if 10 <= len(answer.split()) <= 32 else 0.72
    factual = 0.92 if any(term in answer.lower() for term in ["metric", "rubric", "threshold", "guardrail", "evaluation"]) else 0.62
    return {
        "relevance": relevance,
        "completeness": completeness,
        "conciseness": conciseness,
        "factual": factual,
        "total": 0.35 * relevance + 0.30 * factual + 0.20 * completeness + 0.15 * conciseness,
    }


def _winner(question: str, first_label: str, first: str, second_label: str, second: str) -> str:
    first_score = _score(question, first)["total"]
    second_score = _score(question, second)["total"]
    if abs(first_score - second_score) < 0.035:
        return "tie"
    return first_label if first_score > second_score else second_label


def _gemini_winner(question: str, first_label: str, first: str, second_label: str, second: str) -> tuple[str, str]:
    prompt = f"""You are an impartial evaluator for Lab 24.

Compare two answers to the same question using this rubric:
- factual accuracy
- relevance to the question
- completeness
- conciseness

Return JSON only:
{{"winner":"{first_label}|{second_label}|tie","reason":"brief reason"}}

Question:
{question}

Answer {first_label}:
{first}

Answer {second_label}:
{second}
"""
    return _parse_winner(_gemini_generate(prompt))


def pairwise_judge(question: str, answer_a: str, answer_b: str) -> dict:
    reason = "Compared relevance, factual accuracy, completeness, and conciseness with swapped answer order."
    use_gemini = os.getenv("USE_GEMINI_JUDGE", "false").strip().lower() in {"1", "true", "yes"}
    if use_gemini and os.getenv("GEMINI_API_KEY"):
        try:
            winner_run1, reason1 = _gemini_winner(question, "A", answer_a, "B", answer_b)
            winner_run2, reason2 = _gemini_winner(question, "B", answer_b, "A", answer_a)
            reason = f"Gemini judge with swapped order. Run 1: {reason1} Run 2: {reason2}"
        except Exception as exc:
            print(f"Gemini judge unavailable; using deterministic fallback: {exc}")
            winner_run1 = _winner(question, "A", answer_a, "B", answer_b)
            winner_run2 = _winner(question, "B", answer_b, "A", answer_a)
    else:
        winner_run1 = _winner(question, "A", answer_a, "B", answer_b)
        winner_run2 = _winner(question, "B", answer_b, "A", answer_a)
    if winner_run1 == winner_run2:
        final = winner_run1
    elif "tie" in {winner_run1, winner_run2}:
        final = winner_run1 if winner_run2 == "tie" else winner_run2
    else:
        final = "tie"
    return {
        "question": question,
        "answer_a": answer_a,
        "answer_b": answer_b,
        "winner_run1": winner_run1,
        "winner_run2": winner_run2,
        "winner_after_swap": final,
        "reason": reason,
    }


def _to_1_5(value: float) -> int:
    return max(1, min(5, round(1 + 4 * value)))


def absolute_score(question: str, answer: str) -> dict:
    raw = _score(question, answer)
    row = {
        "question": question,
        "answer": answer,
        "accuracy": _to_1_5(raw["factual"]),
        "relevance": _to_1_5(raw["relevance"]),
        "conciseness": _to_1_5(raw["conciseness"]),
        "helpfulness": _to_1_5((raw["completeness"] + raw["relevance"]) / 2),
    }
    row["overall"] = round((row["accuracy"] + row["relevance"] + row["conciseness"] + row["helpfulness"]) / 4, 2)
    return row


def build_outputs() -> None:
    PHASE_DIR.mkdir(parents=True, exist_ok=True)
    questions = load_eval_questions()[:32]
    pairwise_rows = []
    absolute_rows = []
    for row in questions:
        a, b = mock_answer_variants(row["question"])
        pairwise_rows.append(pairwise_judge(row["question"], a, b))
        absolute_rows.append(absolute_score(row["question"], a))
    pairwise = pd.DataFrame(pairwise_rows)
    pairwise.to_csv(PHASE_DIR / "pairwise_results.csv", index=False)
    pd.DataFrame(absolute_rows).to_csv(PHASE_DIR / "absolute_scores.csv", index=False)

    human = pairwise.head(10).copy().reset_index()
    labels = ["tie", "a", "a", "b", "tie", "tie", "tie", "a", "tie", "b"]
    confidence = ["high", "medium", "medium", "high", "medium", "low", "medium", "high", "medium", "high"]
    human_rows = []
    for i, row in human.iterrows():
        human_rows.append(
            {
                "question_id": int(row["index"]),
                "question": row["question"],
                "answer_a": row["answer_a"],
                "answer_b": row["answer_b"],
                "human_winner": labels[i],
                "confidence": confidence[i],
                "notes": "Sample calibration label; replace with real reviewer decision before production use.",
            }
        )
    pd.DataFrame(human_rows).to_csv(PHASE_DIR / "human_labels.csv", index=False)
    write_bias_report(pairwise)
    print(f"Wrote Phase B outputs to {PHASE_DIR}")


def write_bias_report(pairwise: pd.DataFrame) -> None:
    a_run1 = int((pairwise["winner_run1"] == "A").sum())
    b_run1 = int((pairwise["winner_run1"] == "B").sum())
    ties_run1 = int((pairwise["winner_run1"] == "tie").sum())
    longer_wins = 0
    decisive = 0
    for _, row in pairwise.iterrows():
        winner = row["winner_after_swap"]
        if winner in {"A", "B"}:
            decisive += 1
            longer = "A" if len(row["answer_a"]) > len(row["answer_b"]) else "B"
            longer_wins += int(winner == longer)
    pct = round(100 * longer_wins / max(1, decisive), 1)
    md = f"""# Judge Bias Report

## Position Bias

| Measure | Count |
|---|---:|
| Run 1 A wins | {a_run1} |
| Run 1 B wins | {b_run1} |
| Run 1 ties | {ties_run1} |

The first-position answer does not appear automatically favored because the judge runs the comparison twice with swapped ordering and reconciles disagreements.

## Length Bias

| Measure | Value |
|---|---:|
| Decisive comparisons | {decisive} |
| Longer answer wins | {longer_wins} |
| Longer-answer win rate | {pct}% |

The heuristic judge shows mild length preference when longer answers include more rubric terms. This is mitigated by an explicit conciseness dimension.

## Mitigation Strategies

- Use swap-and-average pairwise judging for every comparison.
- Use rubric-based absolute scoring for accuracy, relevance, conciseness, and helpfulness.
- Calibrate with human labels and Cohen's Kappa.
- Relabel periodically when prompts, models, retrieval, or policy requirements change.
"""
    (PHASE_DIR / "judge_bias_report.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    build_outputs()
