# Lab 24 — Full Evaluation & Guardrail System

## Overview

This project is a complete starter submission for Lab 24 without bonus items. It implements the full evaluation and guardrail system expected for a production-style RAG application: reviewed test-set generation, RAGAS-style evaluation, failure analysis, LLM-as-judge comparison, calibration with Cohen's Kappa, input guardrails, output guardrails, adversarial testing, latency benchmarking, CI/CD evaluation gating, and an operations blueprint. The repository is intentionally organized by phase so each part can be inspected and rerun independently.

The code is designed to run locally on Windows with Python 3.10+. It uses deterministic fallback logic whenever real API keys, RAGAS configuration, Presidio NER, Gemini, or Groq are unavailable. That makes the submission reproducible for grading while still showing where real production services would connect. The main integration point for your real Day 18 RAG pipeline is `phase-a/rag_pipeline.py`, where the mock `rag_pipeline()` function can be replaced while preserving the same return shape.

The generated artifacts are already included: test set, RAGAS results, summary JSON, failure analysis, pairwise judge outputs, absolute scores, human labels, bias report, PII tests, adversarial tests, latency benchmark, and blueprint. The default grading path is local and fast. Live Gemini judging, Groq output guarding, and Presidio NER are all opt-in through environment variables so they do not introduce network failures or variable scores during submission review.

The Day 18 pipeline artifact is integrated under `day18_c401/lab18_C401_F1-main`. Lab 24 uses its `test_set.json`, PDF corpus, and prior RAGAS report contexts through a lightweight adapter in `phase-a/rag_pipeline.py`. The full Day 18 dense pipeline can still be run separately when Qdrant/model dependencies are available, but Lab 24 defaults to a local retrieval adapter so evaluation remains reproducible on Windows.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Optional environment variables:

- `GEMINI_API_KEY` for Gemini-backed LLM judge calls
- `GEMINI_MODEL` defaults to `gemini-2.5-flash-lite`
- `USE_GEMINI_JUDGE=true` enables live Gemini judging; leave it `false` for reproducible grading
- `GROQ_API_KEY` for a hosted Groq output guard classifier
- `GROQ_GUARD_MODEL` defaults to `llama-3.1-8b-instant`
- `USE_GROQ_GUARD=true` enables live Groq output safety calls; leave it `false` for reproducible grading
- `LANGSMITH_API_KEY` for tracing if you add LangSmith integration
- `USE_PRESIDIO=true` enables Presidio NER for input PII detection; leave it `false` for fast grading runs

Some optional packages such as `ragas` and `presidio-analyzer` may install additional dependencies. The starter still runs with fallback logic when those packages or keys are unavailable. `OPENAI_API_KEY` is not required for this version.

## How to Run

First move into the correct project folder:

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
```

Then run the full lab workflow:

```powershell
python phase-a/generate_testset.py
python phase-a/run_ragas_eval.py
python phase-a/analyze_failures.py
python phase-b/judge_pairwise.py
python phase-b/kappa_analysis.py
python phase-b/cross_judge.py
python phase-c/input_guard.py
python phase-c/output_guard.py
python phase-c/full_pipeline.py
```

Or run everything as a single PowerShell copy-paste block:

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
python phase-a/generate_testset.py
python phase-a/run_ragas_eval.py
python phase-a/analyze_failures.py
python phase-b/judge_pairwise.py
python phase-b/kappa_analysis.py
python phase-b/cross_judge.py
python phase-c/input_guard.py
python phase-c/output_guard.py
python phase-c/full_pipeline.py
```

If you are using the local virtual environment, use:

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
.\.venv\Scripts\python.exe phase-a/generate_testset.py
.\.venv\Scripts\python.exe phase-a/run_ragas_eval.py
.\.venv\Scripts\python.exe phase-a/analyze_failures.py
.\.venv\Scripts\python.exe phase-b/judge_pairwise.py
.\.venv\Scripts\python.exe phase-b/kappa_analysis.py
.\.venv\Scripts\python.exe phase-b/cross_judge.py
.\.venv\Scripts\python.exe phase-c/input_guard.py
.\.venv\Scripts\python.exe phase-c/output_guard.py
.\.venv\Scripts\python.exe phase-c/full_pipeline.py
```

### Run Separately

From this folder:

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
```

Phase A:

```powershell
python phase-a/generate_testset.py
python phase-a/run_ragas_eval.py
python phase-a/analyze_failures.py
```

Phase B:

```powershell
python phase-b/judge_pairwise.py
python phase-b/kappa_analysis.py
python phase-b/cross_judge.py
```

Phase C:

```powershell
python phase-c/input_guard.py
python phase-c/output_guard.py
python phase-c/full_pipeline.py
```

Final grading dry-run:

```powershell
python phase-a/run_ragas_eval.py --gate
python phase-b/kappa_analysis.py
python phase-b/cross_judge.py
python phase-c/full_pipeline.py
```

Review the final checklist:

```powershell
notepad SUBMISSION_CHECKLIST.md
```

### Push to GitHub

After creating an empty GitHub repository, push this local commit:

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
git branch -M main
git remote add origin https://github.com/104221795/lab24_eval_guardrail_TruongMinhSon
git push -u origin main
```

Do not commit `.env`; `.gitignore` excludes it.

## Bonus Items

This repository includes three optional bonus deliverables in addition to the required Lab 24 work.

| Bonus | Points | Proof |
|---|---:|---|
| Cross-judge protocol | +3 | `phase-b/cross_judge.py`, `phase-b/cross_judge_results.csv`, `phase-b/cross_judge_summary.json`, `phase-b/cross_judge_report.md` |
| Eval dashboard | +3 | `dashboard/app.py`, `dashboard/README.md`, `requirements-dashboard.txt` |
| Blog post draft | +2 | `blog/lab24-full-eval-guardrails-post.md`, `blog/README.md` |

Run the cross-judge protocol:

```powershell
python phase-b/cross_judge.py
```

Run the optional dashboard:

```powershell
pip install -r requirements-dashboard.txt
streamlit run dashboard/app.py
```

To claim the public blog bonus, publish `blog/lab24-full-eval-guardrails-post.md` to Medium, dev.to, GitHub Pages, or the course forum, then add the public URL here:

```text
Blog URL: TODO
```

## Results Summary

- Phase A: `ragas_summary.json` contains aggregate faithfulness, answer relevancy, context precision, and context recall for 52 questions.
- Phase A simulated evaluation cost: `$0.18`, below the required `$0.50` budget.
- Phase A Day 18 corpus: `phase-a/day18_corpus_manifest.json` documents 2 source PDFs, 41 source PDF pages, and 52 derived text evidence pages/chunks used for evaluation.
- Phase B: `judge_bias_report.md` documents position bias, length bias, and Cohen's Kappa calibration from 10 sample human labels.
- Bonus cross-judge protocol: `cross_judge_summary.json` currently evaluates 30 questions with 3 judge profiles and mean agreement `0.989`.
- Phase C: `pii_test_results.csv`, `adversarial_test_results.csv`, and `latency_benchmark.csv` document PII recall, adversarial detection rate, and P50/P95/P99 timings.
- Phase D: see `phase-d/blueprint.md` for SLOs, architecture, alert playbooks, and monthly cost analysis. The blueprint estimates about `$330/month` for 100k queries/month.

## Demo Video

For a 5-minute demo, show:

1. RAGAS running on 5 questions from `testset_v1.csv`.
2. LLM judge comparing 2 answer versions with swapped positions.
3. Adversarial tests with 3 attacks: DAN, ignore previous instructions, and base64 bypass.
4. Latency benchmark output and layer timing summary.
Video link : https://youtu.be/Zv-Ef6ME0eE
Video backup link : https://www.youtube.com/watch?v=tkSIgRK6Av4

## Reflection

This lab demonstrates that evaluation and guardrails need to be treated as an integrated production system. Quality metrics catch retrieval and generation regressions, while guardrails reduce privacy and safety risk before and after the model call.

The weakest part of a mock starter is that heuristic scores are not a substitute for real RAGAS, human review, or a production safety classifier. The fallback is useful for reproducibility and CI, but real systems should use actual traces, real corpora, and calibrated human labels.

Next improvements should plug in the Day 18 RAG pipeline, replace sample labels with real reviewers, add a stronger retrieval evaluator, and connect monitoring dashboards to the SLOs in the blueprint.
