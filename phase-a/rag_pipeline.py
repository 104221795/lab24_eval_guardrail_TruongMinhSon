"""Replaceable RAG pipeline interface for Lab 24.

The default implementation is deterministic and local so the lab can run
without API keys. It is intentionally small and easy to swap with a real
Day 18 RAG implementation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeItem:
    topic: str
    context: str
    ground_truth: str
    keywords: tuple[str, ...]


KNOWLEDGE_BASE: list[KnowledgeItem] = [
    KnowledgeItem(
        "rag evaluation",
        "RAG evaluation checks faithfulness, answer relevancy, context precision, and context recall against a reviewed test set.",
        "RAG evaluation measures whether answers are grounded, relevant, and supported by retrieved context.",
        ("rag", "evaluation", "faithfulness", "relevancy", "precision", "recall"),
    ),
    KnowledgeItem(
        "guardrails",
        "A guardrail stack commonly includes input validation, PII redaction, injection detection, output safety checks, and audit logging.",
        "Guardrails reduce unsafe inputs and outputs by validating scope, redacting PII, blocking attacks, and checking final responses.",
        ("guardrail", "guardrails", "safety", "scope", "audit"),
    ),
    KnowledgeItem(
        "pii detection",
        "PII detection should catch emails, phone numbers, citizen IDs, bank numbers, and names before sensitive text reaches logs or model calls.",
        "PII detection finds and redacts sensitive identifiers such as emails, phone numbers, IDs, bank accounts, and names.",
        ("pii", "email", "phone", "cccd", "citizen", "bank", "name"),
    ),
    KnowledgeItem(
        "llm-as-judge",
        "LLM-as-judge systems should use rubrics, pairwise comparison, position swaps, and human calibration to reduce bias.",
        "LLM judges compare or score answers using a rubric, then calibrate against human labels to measure agreement.",
        ("judge", "pairwise", "rubric", "kappa", "calibration", "bias"),
    ),
    KnowledgeItem(
        "latency benchmark",
        "Latency benchmarks should report P50, P95, and P99 by layer so guardrail overhead and RAG latency are visible.",
        "Latency benchmarking measures percentiles such as P50, P95, and P99 for each pipeline layer and total runtime.",
        ("latency", "benchmark", "p50", "p95", "p99", "overhead"),
    ),
    KnowledgeItem(
        "ci/cd eval gate",
        "A CI/CD evaluation gate runs tests on pull requests and blocks merges when quality metrics fall below minimum thresholds.",
        "A CI/CD eval gate automatically runs evaluation and fails builds when metrics fall below configured thresholds.",
        ("ci", "cd", "cicd", "gate", "threshold", "workflow", "pull request"),
    ),
    KnowledgeItem(
        "blueprint slos",
        "Blueprint SLOs define targets, alert thresholds, severity, playbooks, and ownership for production evaluation systems.",
        "Blueprint SLOs document targets, alert thresholds, severity, cost, architecture, and incident response.",
        ("blueprint", "slo", "alert", "playbook", "severity", "cost"),
    ),
]


def _match_items(question: str, limit: int = 2) -> list[KnowledgeItem]:
    q = question.lower()
    scored = []
    for item in KNOWLEDGE_BASE:
        score = sum(1 for keyword in item.keywords if keyword in q)
        scored.append((score, item))
    matched = [item for score, item in sorted(scored, key=lambda x: x[0], reverse=True) if score > 0]
    return (matched or [KNOWLEDGE_BASE[0]])[:limit]


def rag_pipeline(question: str) -> dict:
    """REPLACE THIS FUNCTION WITH YOUR DAY 18 RAG PIPELINE.

    Keep the return shape stable:
    {"question": str, "answer": str, "contexts": list[str], "ground_truth": str}
    """

    items = _match_items(question)
    contexts = [item.context for item in items]
    ground_truth = " ".join(item.ground_truth for item in items)
    if len(items) > 1:
        answer = f"{items[0].ground_truth} It should be combined with {items[1].topic} controls for a production-ready system."
    else:
        answer = items[0].ground_truth

    # Intentional imperfections create useful failure-analysis examples.
    if "hybrid" in question.lower() or "chunking" in question.lower():
        answer = "The system should improve retrieval quality and reranking, but exact tuning depends on the corpus."
        contexts = contexts[:1]

    return {
        "question": question,
        "answer": answer,
        "contexts": contexts,
        "ground_truth": ground_truth,
    }


def load_eval_questions() -> list[dict]:
    """Return 52 reviewed questions: 26 simple, 13 reasoning, 13 multi-context."""

    simple = [
        ("What does faithfulness measure in RAG evaluation?", "RAG evaluation measures whether answers are grounded in retrieved context."),
        ("What does answer relevancy measure?", "Answer relevancy measures whether the answer addresses the user's question."),
        ("Why is context precision important?", "Context precision measures whether retrieved chunks are useful and on topic."),
        ("Why is context recall important?", "Context recall measures whether needed evidence was retrieved."),
        ("What is a guardrail stack?", "A guardrail stack validates inputs, redacts PII, detects attacks, checks outputs, and logs events."),
        ("What is PII detection?", "PII detection finds sensitive identifiers such as email, phone, IDs, and bank numbers."),
        ("What is LLM-as-judge?", "LLM-as-judge uses a model and rubric to score or compare answers."),
        ("Why use pairwise judging?", "Pairwise judging compares two answers and can be easier than assigning absolute scores."),
        ("What is Cohen's Kappa used for?", "Cohen's Kappa measures agreement between judge labels and human labels."),
        ("What is a latency benchmark?", "A latency benchmark reports timing percentiles such as P50, P95, and P99."),
        ("What is an evaluation gate in CI/CD?", "A CI/CD eval gate blocks merges when quality metrics fall below thresholds."),
        ("What should blueprint SLOs include?", "Blueprint SLOs include targets, alert thresholds, severity, and playbooks."),
        ("Name one input guardrail.", "PII redaction is an input guardrail."),
        ("Name one output guardrail.", "A safety classifier is an output guardrail."),
        ("What is prompt injection detection?", "Prompt injection detection blocks attempts to override instructions or reveal hidden prompts."),
        ("What should be excluded from audit logs?", "Raw PII should be excluded from audit logs."),
        ("What metric target is used for faithfulness?", "Faithfulness target is at least 0.85 with a minimum acceptable value of 0.75."),
        ("What metric target is used for answer relevancy?", "Answer relevancy target is at least 0.80 with a minimum acceptable value of 0.70."),
        ("What metric target is used for context precision?", "Context precision target is at least 0.70 with a minimum acceptable value of 0.60."),
        ("What metric target is used for context recall?", "Context recall target is at least 0.75 with a minimum acceptable value of 0.65."),
        ("Why redact PII before model calls?", "PII should be redacted before model calls to reduce privacy risk."),
        ("Why run adversarial tests?", "Adversarial tests verify that jailbreaks and prompt injection attempts are blocked."),
        ("Why report P95 latency?", "P95 latency captures slow user experiences better than the average."),
        ("What is a refusal response?", "A refusal response safely declines unsafe requests while offering a compliant alternative."),
        ("What is retrieval metadata filtering?", "Metadata filtering restricts retrieval to relevant topics, sources, or document types."),
        ("What is a reranker?", "A reranker reorders retrieved chunks to put the strongest evidence first."),
    ]
    reasoning = [
        ("If faithfulness is high but context recall is low, what likely happened?", "The answer may be grounded in retrieved chunks, but retrieval missed some required evidence."),
        ("Why combine pairwise judging with human calibration?", "Pairwise judging provides scalable labels, while human calibration measures reliability and bias."),
        ("How can a CI/CD gate prevent RAG regressions?", "It runs evaluation on pull requests and fails when metrics fall below minimum thresholds."),
        ("Why might increasing top_k improve recall but hurt precision?", "More chunks can include missing evidence but also add irrelevant context."),
        ("How do PII redaction and audit logging work together?", "Redaction removes sensitive data before logs store sanitized inputs and decisions."),
        ("Why should an output guard run after the RAG answer is generated?", "It can catch unsafe or private content that appears in the final response."),
        ("When should a reranker be added to retrieval?", "A reranker is useful when initial retrieval returns relevant chunks but not at the top."),
        ("Why can length bias affect LLM judges?", "Judges may prefer longer answers even when concise answers are more accurate."),
        ("How does swap-and-average reduce position bias?", "It judges both answer orders and resolves inconsistent wins as ties or calibrated choices."),
        ("Why measure latency by guardrail layer?", "Layer timing identifies whether input guard, RAG, or output guard causes overhead."),
        ("How should a low precision cluster be fixed?", "Use metadata filters, hybrid retrieval, or reranking to remove off-topic chunks."),
        ("Why is deterministic fallback useful in this lab?", "It makes scripts reproducible when API keys or external services are unavailable."),
        ("Why should topic validation occur before RAG?", "It prevents out-of-scope requests from consuming retrieval and generation resources."),
    ]
    multi_context = [
        ("How do RAGAS metrics and CI/CD gates work together?", "RAGAS metrics quantify quality, and CI/CD gates fail builds below thresholds."),
        ("How should a blueprint connect SLOs, alerts, and evaluation results?", "Blueprints define SLO targets, alert thresholds, and playbooks informed by evaluation results."),
        ("How do input guards, output guards, and audit logs reduce risk?", "Input guards block or sanitize requests, output guards check answers, and audit logs record sanitized decisions."),
        ("How do LLM judge calibration and Cohen's Kappa support trust?", "Calibration compares judge decisions with human labels, and Kappa quantifies agreement."),
        ("How can latency benchmarks include both guardrails and RAG?", "Benchmarks record L1, L2, L3, and total timings across many requests."),
        ("How do PII detection and prompt injection detection differ?", "PII detection redacts sensitive data, while injection detection blocks instruction override attacks."),
        ("How can hybrid search and reranking improve failure clusters?", "Hybrid search improves candidate recall, and reranking improves ordering and precision."),
        ("How should cost analysis account for RAGAS and judge usage?", "Cost analysis estimates generation, sampled RAGAS eval, judge comparisons, guardrails, and storage."),
        ("How does output safety relate to unsafe medical or financial certainty?", "Output guards should flag high-stakes certainty and require safer qualified responses."),
        ("How can manual review improve generated testsets?", "Manual review removes ambiguous questions and ensures distribution across simple, reasoning, and multi-context cases."),
        ("How do blueprint SLOs guide incident playbooks?", "SLO breaches trigger severity, investigation, resolution, and impact tracking steps."),
        ("How should retrieved contexts be logged safely?", "Only sanitized inputs, metadata, timings, and decisions should be logged; raw PII should not be stored."),
        ("How do guardrail detection rate and false positive rate balance?", "Detection rate measures caught attacks, while false positive rate measures valid requests incorrectly blocked."),
    ]
    rows = []
    for question, ground_truth in simple:
        rows.append({"question": question, "ground_truth": ground_truth, "evolution_type": "simple"})
    for question, ground_truth in reasoning:
        rows.append({"question": question, "ground_truth": ground_truth, "evolution_type": "reasoning"})
    for question, ground_truth in multi_context:
        rows.append({"question": question, "ground_truth": ground_truth, "evolution_type": "multi_context"})
    return rows
