from __future__ import annotations

from pathlib import Path

import pandas as pd


PHASE_DIR = Path(__file__).resolve().parent
METRICS = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]


def markdown_table(df: pd.DataFrame) -> str:
    headers = [str(col) for col in df.columns]
    rows = [[str(value) for value in row] for row in df.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def example_list(series: pd.Series, n: int = 2) -> str:
    examples = [str(item) for item in series.dropna().head(n).tolist()]
    while len(examples) < n:
        examples.append("No additional low-scoring example available in this cluster.")
    return "\n".join(f"- {item}" for item in examples)


def main() -> None:
    path = PHASE_DIR / "ragas_results.csv"
    if not path.exists():
        import run_ragas_eval

        run_ragas_eval.run_eval()
    df = pd.read_csv(path)
    df["Average"] = df[METRICS].mean(axis=1).round(3)
    bottom = df.nsmallest(10, "Average").copy()
    bottom.insert(0, "#", range(1, len(bottom) + 1))
    table = bottom[
        ["#", "question", "evolution_type", "faithfulness", "answer_relevancy", "context_precision", "context_recall", "Average"]
    ].rename(
        columns={
            "question": "Question",
            "evolution_type": "Type",
            "faithfulness": "Faithfulness",
            "answer_relevancy": "Answer Relevancy",
            "context_precision": "Context Precision",
            "context_recall": "Context Recall",
        }
    )
    md = [
        "# Failure Cluster Analysis",
        "",
        "## Bottom 10 Questions",
        "",
        markdown_table(table),
        "",
        "## Clusters Identified",
        "",
        "### Cluster C1: Multi-hop reasoning failures",
        "",
        "Pattern: reasoning and multi-context questions lose answer relevancy when the answer compresses multiple requirements into a generic response.",
        "",
        "Example questions:",
        "",
        example_list(bottom[bottom["evolution_type"] != "simple"]["question"], 2),
        "",
        "Root cause: the mock retriever does not rewrite multi-step questions into topic-specific subqueries.",
        "",
        "Proposed technical fix: add query rewriting that decomposes multi-hop questions, retrieve top_k=5 per subquery, then rerank merged candidates.",
        "",
        "### Cluster C2: Off-topic retrieval / weak context precision",
        "",
        "Pattern: retrieved contexts sometimes include broad evaluation text when the question asks for a narrow guardrail or CI/CD detail.",
        "",
        "Example questions:",
        "",
        example_list(bottom.sort_values("context_precision")["question"], 2),
        "",
        "Root cause: keyword-only retrieval has no metadata filter for topic or artifact type.",
        "",
        "Proposed technical fix: use hybrid search BM25 + vector retrieval with metadata filtering by topic, then apply a cross-encoder reranker.",
        "",
        "### Cluster C3: Low context recall",
        "",
        "Pattern: answers that require two concepts are sometimes supported by only one retrieved chunk.",
        "",
        "Example questions:",
        "",
        example_list(bottom.sort_values("context_recall")["question"], 2),
        "",
        "Root cause: chunk selection is capped too tightly and does not enforce coverage diversity.",
        "",
        "Proposed technical fix: tune top_k from 3 to 5, use 500-token chunks with 80-token overlap, and enforce one chunk per predicted topic.",
    ]
    out = PHASE_DIR / "failure_analysis.md"
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
