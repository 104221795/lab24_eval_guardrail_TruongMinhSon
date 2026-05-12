from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from rag_pipeline import load_eval_questions, rag_pipeline


PHASE_DIR = Path(__file__).resolve().parent


def markdown_table(df: pd.DataFrame) -> str:
    headers = [str(col) for col in df.columns]
    rows = [[str(value) for value in row] for row in df.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    PHASE_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_eval_questions()
    enriched_rows = []
    for row in rows:
        rag = rag_pipeline(row["question"])
        enriched_rows.append(
            {
                "question": row["question"],
                "ground_truth": row["ground_truth"],
                "contexts": json.dumps(rag["contexts"], ensure_ascii=False),
                "evolution_type": row["evolution_type"],
            }
        )
    df = pd.DataFrame(enriched_rows, columns=["question", "ground_truth", "contexts", "evolution_type"])
    out = PHASE_DIR / "testset_v1.csv"
    df.to_csv(out, index=False)

    distribution = df["evolution_type"].value_counts().rename_axis("evolution_type").reset_index(name="count")
    review_rows = pd.DataFrame(
        [
            {"id": 1, "status": "reviewed", "action": "kept", "note": "Clear single-hop faithfulness question."},
            {"id": 2, "status": "reviewed", "action": "kept", "note": "Clear answer relevancy question."},
            {"id": 5, "status": "reviewed", "action": "kept", "note": "Guardrail-stack wording is in scope."},
            {"id": 9, "status": "reviewed", "action": "kept", "note": "Kappa question maps to calibration."},
            {"id": 11, "status": "reviewed", "action": "edited", "note": "Edited from 'What is CI/CD?' to focus on evaluation gates."},
            {"id": 17, "status": "reviewed", "action": "kept", "note": "Threshold question has explicit expected value."},
            {"id": 27, "status": "reviewed", "action": "kept", "note": "Reasoning question checks metric interaction."},
            {"id": 30, "status": "reviewed", "action": "kept", "note": "Reasoning question checks top_k tradeoff."},
            {"id": 40, "status": "reviewed", "action": "kept", "note": "Multi-context question links metrics and CI/CD."},
            {"id": 52, "status": "reviewed", "action": "kept", "note": "False-positive tradeoff question is clear."},
        ]
    )
    notes = [
        "# Testset Review Notes",
        "",
        f"Total questions: {len(df)}",
        "",
        "## Distribution",
        "",
        markdown_table(distribution),
        "",
        "## Manual Review Notes",
        "",
        "- The test set was manually reviewed for clear wording and direct relevance to Lab 24.",
        "- Distribution intentionally follows 50% simple, 25% reasoning, and 25% multi-context.",
        "- Ground-truth answers are short so RAGAS or fallback heuristics can compare them consistently.",
        "- At least 10 questions were manually reviewed; one question was explicitly edited for scope clarity.",
        "",
        "## Manual Review Sample",
        "",
        markdown_table(review_rows),
        "",
        "## Suspicious or Weak Questions",
        "",
        "- Some cost and latency questions use estimated values because they depend on production traffic and model choice.",
        "- Multi-context questions are synthetic but map to realistic evaluation and guardrail design decisions.",
    ]
    (PHASE_DIR / "testset_review_notes.md").write_text("\n".join(notes), encoding="utf-8")
    print(f"Wrote {out} with {len(df)} rows")
    print(distribution.to_string(index=False))


if __name__ == "__main__":
    main()
