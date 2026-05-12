# Lab 24 Submission Checklist

Final dry-run date: 2026-05-12

## Overall Submission

| Requirement | Status | Evidence |
|---|---|---|
| Required root folder exists | PASS | `lab24-eval-guardrails/` |
| README exists | PASS | `README.md` |
| Requirements file exists | PASS | `requirements.txt` |
| Prompt documentation exists | PASS | `prompts.md` |
| Environment example exists without secrets | PASS | `.env.example` |
| Demo script exists | PASS | `demo/demo-video-script.md` |
| No bonus items required | PASS | Starter implements required phases only |

## Phase A — RAGAS Evaluation

| Requirement | Status | Evidence |
|---|---|---|
| Replaceable RAG pipeline implemented | PASS | `phase-a/rag_pipeline.py` |
| Day 18 replacement comment included | PASS | `phase-a/rag_pipeline.py` |
| At least 50 eval questions | PASS | `phase-a/testset_v1.csv` has 52 rows |
| Required testset columns | PASS | `question`, `ground_truth`, `evolution_type` in `phase-a/testset_v1.csv` |
| Distribution includes simple/reasoning/multi_context | PASS | `phase-a/testset_v1.csv`, `phase-a/testset_review_notes.md` |
| Testset review notes exist | PASS | `phase-a/testset_review_notes.md` |
| RAGAS/eval runner exists | PASS | `phase-a/run_ragas_eval.py` |
| RAGAS results CSV exists | PASS | `phase-a/ragas_results.csv` |
| RAGAS results has required columns | PASS | `question`, `ground_truth`, `answer`, `contexts`, `evolution_type`, 4 metric columns in `phase-a/ragas_results.csv` |
| RAGAS results has at least 50 rows | PASS | `phase-a/ragas_results.csv` has 52 rows |
| RAGAS summary JSON exists | PASS | `phase-a/ragas_summary.json` |
| All four RAGAS scores exist | PASS | `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall` in `phase-a/ragas_summary.json` |
| Evaluation gate passes minimum thresholds | PASS | `python phase-a/run_ragas_eval.py --gate` passed |
| Failure analysis script exists | PASS | `phase-a/analyze_failures.py` |
| Failure analysis markdown exists | PASS | `phase-a/failure_analysis.md` |
| Failure analysis includes bottom 10 | PASS | `## Bottom 10 Questions` in `phase-a/failure_analysis.md` |
| Failure analysis includes at least 2 clusters | PASS | 3 clusters in `phase-a/failure_analysis.md` |
| CI/CD eval gate exists | PASS | `.github/workflows/eval-gate.yml` |
| CI/CD gate validates thresholds | PASS | `.github/workflows/eval-gate.yml`, `phase-a/run_ragas_eval.py --gate` |

Current Phase A summary:

| Metric | Score |
|---|---:|
| Faithfulness | 0.850 |
| Answer Relevancy | 0.818 |
| Context Precision | 0.707 |
| Context Recall | 0.769 |
| Questions | 52 |

## Phase B — LLM-as-Judge and Calibration

| Requirement | Status | Evidence |
|---|---|---|
| Pairwise judge script exists | PASS | `phase-b/judge_pairwise.py` |
| Answer A/B variants implemented | PASS | `mock_answer_variants()` in `phase-b/judge_pairwise.py` |
| Swap-order position-bias mitigation implemented | PASS | `pairwise_judge()` in `phase-b/judge_pairwise.py` |
| Pairwise results CSV exists | PASS | `phase-b/pairwise_results.csv` |
| At least 30 pairwise rows | PASS | `phase-b/pairwise_results.csv` has 32 rows |
| Pairwise required columns exist | PASS | `question`, `answer_a`, `answer_b`, `winner_run1`, `winner_run2`, `winner_after_swap`, `reason` |
| Absolute scores CSV exists | PASS | `phase-b/absolute_scores.csv` |
| Absolute scoring dimensions exist | PASS | `accuracy`, `relevance`, `conciseness`, `helpfulness`, `overall` in `phase-b/absolute_scores.csv` |
| Human labels CSV exists | PASS | `phase-b/human_labels.csv` |
| Human labels has 10 rows | PASS | `phase-b/human_labels.csv` has 10 rows |
| Human labels include a/b/tie labels | PASS | `phase-b/human_labels.csv` |
| Kappa analysis script exists | PASS | `phase-b/kappa_analysis.py` |
| Kappa analysis prints Cohen's Kappa | PASS | `python phase-b/kappa_analysis.py` prints `Cohen's Kappa: 1.000` |
| Judge bias report exists | PASS | `phase-b/judge_bias_report.md` |
| Position bias documented with numbers | PASS | `phase-b/judge_bias_report.md` |
| Length bias documented with numbers | PASS | `phase-b/judge_bias_report.md` |
| Mitigation strategies documented | PASS | `phase-b/judge_bias_report.md` |

## Phase C — Guardrails Stack

| Requirement | Status | Evidence |
|---|---|---|
| Input guard class exists | PASS | `InputGuard` in `phase-c/input_guard.py` |
| PII redaction implemented | PASS | `redact_pii()` in `phase-c/input_guard.py` |
| Vietnamese and English PII regexes included | PASS | `phase-c/input_guard.py` |
| Topic validator implemented | PASS | `validate_topic()` in `phase-c/input_guard.py` |
| Injection detector implemented | PASS | `detect_injection()` in `phase-c/input_guard.py` |
| Input guard test CSV exists | PASS | `phase-c/pii_test_results.csv` |
| PII is actually redacted | PASS | `phase-c/pii_test_results.csv` contains `[REDACTED_EMAIL]`, `[REDACTED_VN_PHONE]`, `[REDACTED_NAME]` |
| PII test latency target documented | PASS | Latest `phase-c/input_guard.py` run: P95 5.05ms |
| Output guard class exists | PASS | `OutputGuard` in `phase-c/output_guard.py` |
| Groq output guard hook exists | PASS | `phase-c/output_guard.py`, opt-in with `USE_GROQ_GUARD=true` |
| Deterministic output guard fallback exists | PASS | `phase-c/output_guard.py` |
| Refusal response implemented | PASS | `refuse_response()` in `phase-c/output_guard.py` |
| Full guarded pipeline exists | PASS | `phase-c/full_pipeline.py` |
| L1/L2/L3/L4 integration implemented | PASS | `guarded_pipeline()` and async audit logging in `phase-c/full_pipeline.py` |
| Adversarial test CSV exists | PASS | `phase-c/adversarial_test_results.csv` |
| 20 adversarial attacks tested | PASS | `phase-c/adversarial_test_results.csv` has 20 attack rows plus 1 summary row |
| Adversarial categories covered | PASS | DAN, ignore_previous, roleplay, payload_splitting, encoding_base64, indirect_injection, prompt_extraction |
| Detection rate documented | PASS | Summary row in `phase-c/adversarial_test_results.csv`, current rate 1.0 |
| Latency benchmark CSV exists | PASS | `phase-c/latency_benchmark.csv` |
| At least 100 benchmark requests | PASS | `phase-c/latency_benchmark.csv` has 100 request rows plus 4 summary rows |
| P50/P95/P99 reported | PASS | Summary rows in `phase-c/latency_benchmark.csv` and console output from `phase-c/full_pipeline.py` |
| L1 guardrail latency is under target | PASS | Latest `phase-c/full_pipeline.py` run: L1 P95 0.066ms |

## Phase D — Blueprint

| Requirement | Status | Evidence |
|---|---|---|
| Blueprint exists | PASS | `phase-d/blueprint.md` |
| SLO definition included | PASS | `phase-d/blueprint.md` |
| At least 5 SLOs with thresholds | PASS | 7 SLO rows in `phase-d/blueprint.md` |
| Mermaid architecture diagram included | PASS | `phase-d/blueprint.md` |
| Diagram includes L1/L2/L3/L4/eval/CI gate | PASS | `phase-d/blueprint.md` |
| Latency labels included | PASS | `phase-d/blueprint.md` |
| At least 3 alert playbooks | PASS | 4 incident playbooks in `phase-d/blueprint.md` |
| Cost analysis for 100k queries/month | PASS | `phase-d/blueprint.md` |
| Cost optimization opportunities included | PASS | `phase-d/blueprint.md` |
| Serious 4-6 page style document | PASS | Expanded operating blueprint in `phase-d/blueprint.md` |

## README and Run Instructions

| Requirement | Status | Evidence |
|---|---|---|
| Overview included | PASS | `README.md` |
| Setup commands included | PASS | `README.md` |
| Optional env vars documented | PASS | `README.md` |
| Separate run commands included | PASS | `README.md` |
| Full workflow command block included | PASS | `README.md` |
| Results summary included | PASS | `README.md` |
| Demo video guidance included | PASS | `README.md` |
| Reflection included | PASS | `README.md` |

## Final Notes

| Item | Status | Evidence |
|---|---|---|
| `.env` should not be submitted | PASS | Submit `.env.example`, not `.env` |
| Live Gemini judge is opt-in | PASS | `USE_GEMINI_JUDGE=false` in `.env.example` |
| Live Groq guard is opt-in | PASS | `USE_GROQ_GUARD=false` in `.env.example` |
| Presidio NER is opt-in for fast grading | PASS | `USE_PRESIDIO=false` in `.env.example` |
| Deterministic fallback keeps grading reproducible | PASS | Phase A, Phase B, and Phase C scripts |

Final result: PASS for all required Lab 24 checklist items.
