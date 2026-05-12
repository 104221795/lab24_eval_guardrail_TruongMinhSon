# Building a Full Evaluation and Guardrail System for a RAG App

_Publication-ready draft for Medium, dev.to, or a course blog._

## Summary

In Lab 24, I built a full evaluation and guardrail layer around a retrieval-augmented generation system. The goal was not just to make a RAG demo work, but to make it measurable, safer, and easier to operate. The final system connects to my Day 18 corpus, generates an evaluation test set, runs RAGAS-style scoring, performs LLM-as-judge calibration, applies input and output guardrails, runs adversarial tests, benchmarks latency, and documents production SLOs in a blueprint.

The system is intentionally reproducible. When API keys are unavailable, it uses deterministic fallback logic so every script still runs locally on Windows. Live Gemini judging, Groq output guarding, and Presidio NER are supported as opt-in extensions, but the default grading path remains stable.

## Day 18 Corpus Integration

The evaluation set is grounded in the Day 18 RAG corpus. The corpus includes two source PDFs: a BCTC tax document and Nghị định 13/2023/NĐ-CP on personal data protection. The source PDFs contain 41 PDF pages, and Lab 24 derives 52 text evidence pages/chunks for evaluation. This gives the evaluation enough coverage to test simple factual questions, reasoning questions, and multi-context questions.

The Day 18 dense pipeline can require Qdrant and local model downloads, so I added a lightweight adapter for Lab 24. The adapter uses the Day 18 test set, PDF evidence, and prior RAGAS report contexts to provide local retrieval behavior without requiring external services during grading.

## Phase A: RAGAS Evaluation

The generated test set contains 52 questions:

- 26 simple questions
- 13 reasoning questions
- 13 multi-context questions

The current RAGAS-style aggregate scores are:

| Metric | Score |
|---|---:|
| Faithfulness | 0.955 |
| Answer Relevancy | 0.933 |
| Context Precision | 0.787 |
| Context Recall | 0.908 |

The evaluation gate fails if any minimum threshold is missed. This makes the evaluation usable in CI/CD rather than just as an offline report.

## Phase B: LLM-as-Judge and Calibration

The judge system includes pairwise comparison, absolute scoring, and human calibration labels. Pairwise judging runs each comparison twice with swapped answer order to reduce position bias. Absolute scoring evaluates accuracy, relevance, conciseness, and helpfulness.

I also added a cross-judge bonus protocol. It uses three judge profiles:

- `accuracy_first`
- `concise_first`
- `completeness_first`

The final winner is selected by majority aggregation. This makes judge behavior easier to inspect because disagreement between judge profiles becomes visible instead of hidden inside one score.

## Phase C: Guardrails

The guardrail stack has four layers:

- L1 input guard: PII redaction, topic validation, injection detection
- L2 RAG/LLM pipeline
- L3 output guard
- L4 async audit logging

The input guard catches Vietnamese and English PII patterns such as emails, phone numbers, CCCD numbers, bank-account-like numbers, and names after phrases like “tôi là” or “my name is.” The output guard checks for harmful instructions, private data leakage, prompt leakage, unsafe high-stakes certainty, violent/hateful content, and jailbreak compliance.

The latest guardrail results are:

- PII recall: 88%
- Adversarial detection: 100%
- Output guard detection: 100%
- Output guard false positive rate: 0%
- L1 P95 latency: below 1ms in local fallback mode
- L3 P95 latency: below 1ms in local fallback mode

## Phase D: Production Blueprint

The blueprint defines production SLOs, alert thresholds, incident playbooks, architecture, and cost estimates. It includes playbooks for faithfulness drops, latency spikes, guardrail detection drops, and false-positive spikes. The cost model estimates about $330/month for 100k monthly queries, with optimizations such as sampling, caching, smaller judge models, and async logging.

## What I Learned

The biggest lesson is that RAG quality is not one metric. Faithfulness, relevancy, precision, and recall tell different stories. A system can retrieve relevant-looking chunks but still miss critical evidence. It can answer fluently but not faithfully. A CI gate helps because it turns these quality checks into a release requirement.

The second lesson is that guardrails should be layered. Input validation alone is not enough because unsafe content can appear in retrieved documents or generated outputs. Output validation alone is not enough because malicious prompts can waste resources or leak into downstream components. Defense in depth is more practical.

The third lesson is that reproducibility matters. In a classroom or CI environment, external APIs can fail or produce variable outputs. Deterministic fallbacks make the project easier to grade and debug, while opt-in live providers keep a path open for production.

## Next Improvements

The next step would be to connect the full Day 18 dense retrieval pipeline in production mode with Qdrant and model-backed generation. I would also replace starter human labels with real reviewer labels, add more Vietnamese adversarial examples, and publish dashboards from CI artifacts automatically.

## Publication Checklist

- Add screenshots from `dashboard/app.py`.
- Add a GitHub repository link.
- Add a short demo video link.
- Publish to Medium, dev.to, or the course forum.
- Add the public URL back to `README.md` if the blog bonus requires a live link.
