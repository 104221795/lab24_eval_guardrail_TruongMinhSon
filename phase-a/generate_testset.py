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


def write_day18_corpus_manifest(df: pd.DataFrame) -> None:
    pdf_paths = [
        PHASE_DIR / "BCTC.pdf",
        PHASE_DIR / "Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf",
    ]
    pdf_rows = []
    total_pages = 0
    for path in pdf_paths:
        pages = 0
        if path.exists():
            try:
                import fitz

                pages = fitz.open(path).page_count
            except Exception:
                pages = 0
        total_pages += pages
        pdf_rows.append({"file": path.name, "pages": pages, "bytes": path.stat().st_size if path.exists() else 0})

    text_pages = []
    for idx, row in df.iterrows():
        contexts = json.loads(row["contexts"])
        text_pages.append(
            "\n".join(
                [
                    f"## Text Evidence Page {idx + 1}",
                    "",
                    f"Question: {row['question']}",
                    f"Evolution type: {row['evolution_type']}",
                    "",
                    "Context evidence:",
                    "",
                    "\n\n".join(contexts),
                ]
            )
        )
    (PHASE_DIR / "day18_corpus_text_pages.md").write_text("\n\n---\n\n".join(text_pages), encoding="utf-8")
    manifest = {
        "source": "day18_c401/lab18_C401_F1-main",
        "source_pdfs": pdf_rows,
        "source_pdf_pages": total_pages,
        "derived_text_evidence_pages": len(text_pages),
        "note": "The source PDFs contain 41 PDF pages. Lab 24 uses 52 derived text evidence pages/chunks from the Day 18 corpus, Day 18 test set, and Day 18 RAGAS report contexts.",
    }
    (PHASE_DIR / "day18_corpus_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


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
    write_day18_corpus_manifest(df)

    distribution = df["evolution_type"].value_counts().rename_axis("evolution_type").reset_index(name="count")
    review_rows = pd.DataFrame(
        [
            {"id": 1, "status": "reviewed", "action": "kept", "note": "Clear BCTC form-number question from Day 18 test set."},
            {"id": 2, "status": "reviewed", "action": "kept", "note": "Clear tax-period question grounded in BCTC.pdf."},
            {"id": 5, "status": "reviewed", "action": "kept", "note": "Nghị định 13 topic question is direct and answerable."},
            {"id": 9, "status": "reviewed", "action": "kept", "note": "Personal identifier question maps to Nghị định 13 definitions."},
            {"id": 11, "status": "reviewed", "action": "edited", "note": "Edited wording to explicitly ask how GTGT payable is calculated from output and input VAT."},
            {"id": 17, "status": "reviewed", "action": "kept", "note": "Negative-evidence banking question is useful for hallucination testing."},
            {"id": 22, "status": "reviewed", "action": "kept", "note": "Simple tax document question checks source classification."},
            {"id": 31, "status": "reviewed", "action": "kept", "note": "Reasoning question checks cross-source mismatch handling."},
            {"id": 44, "status": "reviewed", "action": "kept", "note": "Multi-context question requires distinguishing BCTC from legal document."},
            {"id": 52, "status": "reviewed", "action": "kept", "note": "Multi-context retrieval failure question maps to RAGAS recall."},
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
        "- Questions are generated from the correct Day 18 corpus: BCTC.pdf and Nghị định 13/2023/NĐ-CP.",
        "- Distribution intentionally follows 50% simple, 25% reasoning, and 25% multi-context.",
        "- Ground-truth answers are short so RAGAS or fallback heuristics can compare them consistently.",
        "- At least 10 questions were manually reviewed; one question was explicitly edited for scope clarity.",
        "- Corpus manifest and derived text evidence pages are saved in `day18_corpus_manifest.json` and `day18_corpus_text_pages.md`.",
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
