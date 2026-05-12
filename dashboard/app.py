from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def load_csv(path: str) -> pd.DataFrame:
    full = ROOT / path
    if not full.exists():
        return pd.DataFrame()
    return pd.read_csv(full)


st.set_page_config(page_title="Lab 24 Eval & Guardrails", layout="wide")
st.title("Lab 24 - Evaluation & Guardrails Dashboard")
st.caption("Reads generated artifacts from Phase A, B, and C. No API keys required.")

ragas_summary = load_json("phase-a/ragas_summary.json")
cross_summary = load_json("phase-b/cross_judge_summary.json")
manifest = load_json("phase-a/day18_corpus_manifest.json")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faithfulness", ragas_summary.get("faithfulness", "n/a"))
col2.metric("Answer Relevancy", ragas_summary.get("answer_relevancy", "n/a"))
col3.metric("Context Precision", ragas_summary.get("context_precision", "n/a"))
col4.metric("Context Recall", ragas_summary.get("context_recall", "n/a"))

col5, col6, col7 = st.columns(3)
col5.metric("Questions", ragas_summary.get("num_questions", "n/a"))
col6.metric("Day 18 PDF Pages", manifest.get("source_pdf_pages", "n/a"))
col7.metric("Cross-Judge Agreement", cross_summary.get("mean_agreement_rate", "n/a"))

tab_a, tab_b, tab_c, tab_d = st.tabs(["RAGAS", "Cross-Judge", "Guardrails", "Corpus"])

with tab_a:
    st.subheader("RAGAS Results")
    ragas = load_csv("phase-a/ragas_results.csv")
    if ragas.empty:
        st.warning("Run `python phase-a/run_ragas_eval.py` first.")
    else:
        metrics = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        st.bar_chart(ragas[metrics].mean())
        ragas["average"] = ragas[metrics].mean(axis=1)
        st.write("Bottom 10 questions by average score")
        st.dataframe(ragas.sort_values("average").head(10), use_container_width=True)

with tab_b:
    st.subheader("Cross-Judge Protocol")
    cross = load_csv("phase-b/cross_judge_results.csv")
    if cross.empty:
        st.warning("Run `python phase-b/cross_judge.py` first.")
    else:
        st.json(cross_summary)
        st.dataframe(cross, use_container_width=True)

with tab_c:
    st.subheader("Guardrail Tests")
    pii = load_csv("phase-c/pii_test_results.csv")
    adv = load_csv("phase-c/adversarial_test_results.csv")
    latency = load_csv("phase-c/latency_benchmark.csv")
    out_guard = load_csv("phase-c/output_guard_test_results.csv")
    c1, c2, c3 = st.columns(3)
    c1.metric("PII Test Rows", len(pii))
    c2.metric("Adversarial Rows", len(adv[adv.get("category", "") != "summary"]) if not adv.empty else 0)
    c3.metric("Latency Requests", pd.to_numeric(latency.get("request_id", pd.Series(dtype=str)), errors="coerce").notna().sum() if not latency.empty else 0)
    st.write("PII Redaction")
    st.dataframe(pii, use_container_width=True)
    st.write("Adversarial Detection")
    st.dataframe(adv, use_container_width=True)
    st.write("Output Guard")
    st.dataframe(out_guard, use_container_width=True)
    st.write("Latency")
    st.dataframe(latency, use_container_width=True)

with tab_d:
    st.subheader("Day 18 Corpus Manifest")
    st.json(manifest)
    evidence_path = ROOT / "phase-a/day18_corpus_text_pages.md"
    if evidence_path.exists():
        st.download_button(
            "Download derived text evidence pages",
            evidence_path.read_text(encoding="utf-8"),
            file_name="day18_corpus_text_pages.md",
        )
