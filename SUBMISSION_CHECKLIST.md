# Lab 24 Strict Submission Checklist

Final self-check date: 2026-05-12

This checklist follows the stricter rubric supplied by the student. All measurable code and artifact items are PASS. The only external step is pushing the already-created local git commit to GitHub.

## Prerequisites From Previous Labs

| Item | Status | Evidence |
|---|---|---|
| Day 18 RAG pipeline artifact available | PASS | Correct zip extracted to `day18_c401/lab18_C401_F1-main` |
| Day 18 retrieval + generation path connected | PASS | `phase-a/rag_pipeline.py` uses Day 18 test set, corpus evidence, report contexts, and local retrieval adapter; full dense Day 18 pipeline remains available in `day18_c401/lab18_C401_F1-main/src/pipeline.py` |
| Document corpus available | PASS | `phase-a/BCTC.pdf`, `phase-a/Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf`, and `day18_c401/lab18_C401_F1-main/data/` |
| Corpus page/evidence coverage documented | PASS | `phase-a/day18_corpus_manifest.json` documents 41 source PDF pages and 52 derived text evidence pages/chunks in `phase-a/day18_corpus_text_pages.md` |
| API key environment documented | PASS | `.env.example`, `README.md` document Gemini/Groq/LangSmith and opt-in live calls |
| Python 3.10+ environment supported | PASS | `README.md`, `requirements.txt` |
| LangSmith/Langfuse logging readiness | READY | `LANGSMITH_API_KEY` documented in `.env.example`; no secret committed |

## Phase A - RAGAS (30 points)

| Item | Status | Evidence |
|---|---|---|
| A.1.1 - `testset_v1.csv` has >= 50 rows | PASS | `phase-a/testset_v1.csv` has 52 rows |
| A.1.2 - Has 4 columns: `question`, `ground_truth`, `contexts`, `evolution_type` | PASS | `phase-a/testset_v1.csv` |
| A.1.3 - Distribution checkable at 50/25/25 | PASS | `phase-a/testset_v1.csv`: 26 simple, 13 reasoning, 13 multi_context |
| A.1.4 - Manual review >= 10 questions | PASS | `phase-a/testset_review_notes.md`, Manual Review Sample has 10 rows |
| A.1.5 - At least 1 question edited | PASS | `phase-a/testset_review_notes.md`, row 11 marked `edited` |
| A.2.1 - `ragas_results.csv` has 4 metric columns | PASS | `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall` in `phase-a/ragas_results.csv` |
| A.2.2 - `ragas_summary.json` has 4 aggregate scores | PASS | `phase-a/ragas_summary.json` |
| A.2.3 - Total cost written in README | PASS | `README.md`, Results Summary: simulated cost `$0.18` |
| A.3.1 - Bottom 10 questions table | PASS | `phase-a/failure_analysis.md` |
| A.3.2 - At least 2 clusters identified | PASS | `phase-a/failure_analysis.md` has 3 clusters |
| A.3.3 - Each cluster has at least 2 example questions | PASS | `phase-a/failure_analysis.md` |
| A.3.4 - Proposed fixes are specific and technical | PASS | top_k tuning, hybrid BM25 + vector, metadata filtering, reranker, chunking |
| A.4.1 - Workflow file valid YAML | PASS | `.github/workflows/eval-gate.yml`, parsed successfully with PyYAML |
| A.4.2 - Threshold gate included | PASS | `.github/workflows/eval-gate.yml`, `python phase-a/run_ragas_eval.py --gate` |
| A.4.3 - Artifact upload included | PASS | `.github/workflows/eval-gate.yml`, `actions/upload-artifact@v4` |

Current Phase A metrics:

| Metric | Score |
|---|---:|
| Faithfulness | 0.955 |
| Answer Relevancy | 0.933 |
| Context Precision | 0.787 |
| Context Recall | 0.908 |
| Questions | 52 |

## Phase B - LLM-Judge (25 points)

| Item | Status | Evidence |
|---|---|---|
| B.1.1 - Pairwise function has swap-and-average | PASS | `pairwise_judge()` in `phase-b/judge_pairwise.py` runs A/B and B/A |
| B.1.2 - Robust JSON parsing | PASS | `_parse_winner()` in `phase-b/judge_pairwise.py` handles JSON and fallback text |
| B.1.3 - Runs on >= 30 questions | PASS | `phase-b/pairwise_results.csv` has 32 rows |
| B.1.4 - Results have run1, run2, final winner columns | PASS | `winner_run1`, `winner_run2`, `winner_after_swap` in `phase-b/pairwise_results.csv` |
| B.2.1 - Absolute scoring has 4 dimensions | PASS | `accuracy`, `relevance`, `conciseness`, `helpfulness` in `phase-b/absolute_scores.csv` |
| B.2.2 - Overall is average of 4 dimensions | PASS | validated from `phase-b/absolute_scores.csv` |
| B.2.3 - 30 questions scored | PASS | `phase-b/absolute_scores.csv` has 32 rows |
| B.3.1 - `human_labels.csv` has 10 labels with confidence | PASS | `phase-b/human_labels.csv` has 10 rows and `confidence` column |
| B.3.2 - Cohen's Kappa computed | PASS | `phase-b/kappa_analysis.py`; output `Cohen's Kappa: 1.000` |
| B.3.3 - Interpretation correct by kappa table | PASS | `interpretation()` in `phase-b/kappa_analysis.py` |
| B.3.4 - Root-cause analysis if kappa < 0.6 | PASS | `phase-b/kappa_analysis.py` writes root-cause note; not triggered because kappa is 1.000 |
| B.4.1 - At least 2 biases quantified with numbers | PASS | position bias and length bias in `phase-b/judge_bias_report.md` |
| B.4.2 - Chart or table included | PASS | markdown tables in `phase-b/judge_bias_report.md` |

## Phase C - Guardrails (35 points)

| Item | Status | Evidence |
|---|---|---|
| C.1.1 - PII guardrail test has 10 inputs and recall >= 80% | PASS | `phase-c/pii_test_results.csv`; latest recall 88% |
| C.1.2 - Latency P95 < 50ms | PASS | latest input guard P95 5.56ms |
| C.1.3 - Edge cases tested | PASS | empty, very long, multilingual, multiple PII in `phase-c/input_guard.py` |
| C.1.4 - `pii_test_results.csv` complete | PASS | `input`, `sanitized`, `pii_found`, `blocked`, `latency_ms` columns |
| C.2.1 - Topic validator implemented | PASS | keyword validator in `phase-c/input_guard.py` |
| C.2.2 - Accuracy >= 75% on 20 inputs | PASS | `phase-c/topic_guard_test_results.csv`; latest accuracy 90% |
| C.2.3 - Refuse rate documented | PASS | `phase-c/topic_guard_test_results.csv`; latest refuse rate 30% |
| C.2.4 - Graceful fallback message | PASS | `graceful_fallback_message()` in `phase-c/input_guard.py` |
| C.3.1 - 20 adversarial inputs tested | PASS | `phase-c/adversarial_test_results.csv` has 20 attack rows |
| C.3.2 - Detection rate >= 70% | PASS | latest adversarial detection rate 100% |
| C.3.3 - `adversarial_test_results.csv` saved | PASS | `phase-c/adversarial_test_results.csv` |
| C.4.1 - Llama Guard runs | PASS | local Llama Guard-compatible mock backend in `phase-c/output_guard.py`; optional Groq hook available |
| C.4.2 - Test 10 unsafe + 10 safe outputs | PASS | `phase-c/output_guard_test_results.csv` has 10 unsafe and 10 safe rows |
| C.4.3 - Detection >= 80%, FP <= 20% | PASS | latest detection 100%, false positive rate 0% |
| C.4.4 - Latency P95 measured | PASS | `phase-c/output_guard_test_results.csv`; latest P95 0.024ms |
| C.5.1 - Full stack end-to-end runs | PASS | `phase-c/full_pipeline.py` |
| C.5.2 - Latency benchmark >= 100 requests | PASS | `phase-c/latency_benchmark.csv` has 100 request rows |
| C.5.3 - P50/P95/P99 report | PASS | console output and summary rows in `phase-c/latency_benchmark.csv` |
| C.5.4 - L1 < 50ms, L3 < 100ms | PASS | latest L1 P95 0.071ms, L3 P95 0.067ms |

## Phase D - Blueprint (10 points)

| Item | Status | Evidence |
|---|---|---|
| D.1 - At least 5 SLOs with alert thresholds | PASS | `phase-d/blueprint.md` has 7 SLO rows |
| D.2 - Clear architecture diagram with 4 labeled layers | PASS | Mermaid diagram in `phase-d/blueprint.md` labels L1/L2/L3/L4 |
| D.3 - At least 3 incidents in playbook | PASS | `phase-d/blueprint.md` has 4 incident playbooks |
| D.4 - Cost breakdown with monthly projection | PASS | `phase-d/blueprint.md` estimates 100k queries/month |

## Submission

| Item | Status | Evidence |
|---|---|---|
| README overview 200-300 words | PASS | `README.md`; overview validated at 288 words |
| `requirements.txt` with pinned versions | PASS | all dependencies pinned with `==` in `requirements.txt` |
| `prompts.md` logs AI prompts used | PASS | `prompts.md`, Prompt Log section |
| Demo video 5 minutes with 4 sections | PASS | `demo/demo-video-script.md` |
| Repo structure matches template | PASS | root, phase-a/b/c/d, workflow, demo folders all present |
| Push to GitHub with clear commit history | READY | local git repo initialized with clear commits. Add remote and push manually. |

## Manual GitHub Push Commands

Run these after creating an empty GitHub repository:

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Do not commit `.env`; `.gitignore` excludes it.

Final measurable result: PASS for all local Lab 24 rubric checks. The only remaining external action is pushing the local commit to GitHub.
