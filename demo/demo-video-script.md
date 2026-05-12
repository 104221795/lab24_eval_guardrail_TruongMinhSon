# Demo Video Script

## 0:00-0:45 Overview

Show the repository structure and explain that the implementation covers RAGAS evaluation, LLM-as-judge calibration, guardrails, and the production blueprint.

## 0:45-1:45 Phase A

Run:

```powershell
python phase-a/generate_testset.py
python phase-a/run_ragas_eval.py
```

Show `testset_v1.csv`, `ragas_results.csv`, and `ragas_summary.json`. Point out that fallback scoring works without API keys and that `rag_pipeline.py` is the Day 18 integration point.

## 1:45-2:45 Phase B

Run:

```powershell
python phase-b/judge_pairwise.py
python phase-b/kappa_analysis.py
```

Show one pairwise comparison, the swapped winners, absolute rubric scores, human labels, and Cohen's Kappa in `judge_bias_report.md`.

## 2:45-4:00 Phase C

Run:

```powershell
python phase-c/input_guard.py
python phase-c/output_guard.py
python phase-c/full_pipeline.py
```

Show three attacks: DAN, ignore previous instructions, and base64 bypass. Show that sanitized inputs are logged instead of raw PII.

## 4:00-5:00 Blueprint

Open `phase-d/blueprint.md`. Highlight SLOs, the Mermaid architecture diagram, alert playbooks, and the cost estimate for 100k monthly queries.
