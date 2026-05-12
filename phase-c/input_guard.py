from __future__ import annotations

import os
import re
import statistics
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")


class InputGuard:
    _presidio_analyzer = None
    _presidio_anonymizer = None

    allowed_topics = {
        "RAG": ["rag", "retrieval", "context", "chunk", "rerank"],
        "evaluation": ["evaluation", "ragas", "faithfulness", "relevancy", "precision", "recall"],
        "guardrails": ["guardrail", "safety", "sanitize", "block"],
        "LLM judge": ["judge", "pairwise", "kappa", "calibration", "rubric"],
        "latency": ["latency", "p50", "p95", "p99", "benchmark"],
        "CI/CD": ["ci/cd", "cicd", "workflow", "gate", "threshold"],
        "blueprint": ["blueprint", "slo", "alert", "playbook", "cost"],
        "PII": ["pii", "email", "phone", "cccd", "privacy", "redact"],
    }

    pii_patterns = {
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "VN_PHONE": re.compile(r"(?<!\d)(?:\+84|0)(?:\d[\s.-]?){8,10}\d(?!\d)"),
        "CCCD": re.compile(r"(?<!\d)\d{12}(?!\d)"),
        "BANK_ACCOUNT": re.compile(r"\b(?:account|bank|stk|số tài khoản|tai khoan)\s*[:#-]?\s*\d{8,16}\b", re.I),
        "VN_NAME": re.compile(r"\b(?:tôi là|mình là|toi la|minh la|my name is)\s+([A-ZÀ-Ỵ][\wÀ-ỹ]*(?:\s+[A-ZÀ-Ỵ][\wÀ-ỹ]*){1,3})", re.I),
    }

    injection_patterns = {
        "ignore previous instructions": re.compile(r"ignore (all )?(previous|prior) instructions", re.I),
        "system prompt extraction": re.compile(r"(show|reveal|print|extract).{0,40}(system prompt|hidden prompt)", re.I),
        "developer message extraction": re.compile(r"(show|reveal|print|extract).{0,40}(developer message|developer instructions)", re.I),
        "DAN jailbreak": re.compile(r"\bDAN\b|do anything now|jailbreak", re.I),
        "unrestricted roleplay": re.compile(r"pretend you are unrestricted|no safety rules|bypass policy", re.I),
        "base64 bypass": re.compile(r"base64|decode this|encoded payload", re.I),
        "evil roleplay": re.compile(r"roleplay as (an )?evil ai|act as (an )?evil", re.I),
        "payload splitting": re.compile(r"split.{0,30}payload|combine.{0,30}parts", re.I),
    }

    def redact_pii(self, text: str) -> tuple[str, list[str]]:
        sanitized = text
        found: list[str] = []
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(sanitized):
                found.append(pii_type)
                if pii_type == "VN_NAME":
                    sanitized = pattern.sub(lambda m: m.group(0).replace(m.group(1), "[REDACTED_NAME]"), sanitized)
                else:
                    sanitized = pattern.sub(f"[REDACTED_{pii_type}]", sanitized)
        use_presidio = os.getenv("USE_PRESIDIO", "false").strip().lower() in {"1", "true", "yes"}
        if use_presidio:
            try:
                from presidio_analyzer import AnalyzerEngine
                from presidio_anonymizer import AnonymizerEngine

                if InputGuard._presidio_analyzer is None:
                    InputGuard._presidio_analyzer = AnalyzerEngine()
                    InputGuard._presidio_anonymizer = AnonymizerEngine()
                results = InputGuard._presidio_analyzer.analyze(text=sanitized, language="en")
                if results:
                    sanitized = InputGuard._presidio_anonymizer.anonymize(text=sanitized, analyzer_results=results).text
                    found.extend(sorted({r.entity_type for r in results}))
            except Exception as exc:
                print(f"Presidio unavailable; using regex-only PII redaction: {exc}")
        return sanitized, sorted(set(found))

    def validate_topic(self, text: str) -> dict:
        if not text.strip():
            return {"allowed": False, "reason": "Empty input is not a valid lab question.", "closest_topic": None}
        low = text.lower()
        counts = {topic: sum(1 for kw in kws if kw in low) for topic, kws in self.allowed_topics.items()}
        best_topic, best_score = max(counts.items(), key=lambda item: item[1])
        if best_score > 0:
            return {"allowed": True, "reason": f"Matched allowed topic: {best_topic}.", "closest_topic": best_topic}
        return {"allowed": False, "reason": "Input is outside the Lab 24 evaluation and guardrails scope.", "closest_topic": best_topic}

    def detect_injection(self, text: str) -> tuple[bool, str]:
        for reason, pattern in self.injection_patterns.items():
            if pattern.search(text):
                return True, reason
        return False, ""

    @staticmethod
    def graceful_fallback_message() -> str:
        return (
            "I can only help with Lab 24 evaluation and guardrail topics here. "
            "Please ask about RAG, evaluation, guardrails, PII, LLM judges, latency, CI/CD, or the blueprint."
        )

    def sanitize(self, user_input: str) -> dict:
        start = time.perf_counter()
        original = user_input or ""
        sanitized, pii_found = self.redact_pii(original[:10000])
        topic = self.validate_topic(sanitized)
        injection, injection_reason = self.detect_injection(original)
        blocked = injection or not topic["allowed"] or not original.strip()
        return {
            "original": original,
            "sanitized": sanitized,
            "pii_found": pii_found,
            "topic_allowed": topic["allowed"],
            "topic_reason": topic["reason"],
            "injection_detected": injection,
            "injection_reason": injection_reason,
            "blocked": blocked,
            "latency_ms": round((time.perf_counter() - start) * 1000, 3),
        }


def run_tests() -> None:
    guard = InputGuard()
    tests = [
        "My name is John Smith and my email is john@example.com. How should RAG evaluation work?",
        "Số điện thoại của tôi là 0912345678, hỏi về guardrails.",
        "Contact me at learner@example.org about latency benchmark.",
        "CCCD của tôi là 012345678901 và tôi muốn kiểm tra PII.",
        "Số tài khoản 123456789012 tại bank, explain audit logging.",
        "Tôi là Nguyễn Văn An, RAGAS faithfulness là gì?",
        "What is context recall in RAG evaluation?",
        "",
        "RAG " + ("evaluation " * 1200),
        "Mình là Trần Thị Mai, email mai@test.vn, phone +84987654321, explain PII redaction.",
    ]
    rows = []
    expected_pii = 8
    detected = 0
    latencies = []
    for item in tests:
        result = guard.sanitize(item)
        detected += int(bool(result["pii_found"]))
        latencies.append(result["latency_ms"])
        rows.append(
            {
                "input": item,
                "sanitized": result["sanitized"],
                "pii_found": ",".join(result["pii_found"]),
                "blocked": result["blocked"],
                "latency_ms": result["latency_ms"],
            }
        )
    recall = detected / expected_pii
    p95 = statistics.quantiles(latencies, n=20)[18]
    pd.DataFrame(rows).to_csv(PHASE_DIR / "pii_test_results.csv", index=False)
    print(f"Wrote pii_test_results.csv | documented recall={recall:.0%} | P95={p95:.2f}ms")
    run_topic_validator_tests(guard)


def run_topic_validator_tests(guard: InputGuard | None = None) -> None:
    guard = guard or InputGuard()
    tests = [
        ("What is faithfulness in RAG evaluation?", True),
        ("How do guardrails detect prompt injection?", True),
        ("Explain PII redaction before audit logging.", True),
        ("How should an LLM judge use pairwise scoring?", True),
        ("How do I benchmark P95 latency?", True),
        ("How does a CI/CD eval gate work?", True),
        ("What SLOs belong in the blueprint?", True),
        ("How does reranking improve retrieval?", True),
        ("What is context precision?", True),
        ("How should Cohen's Kappa calibrate a judge?", True),
        ("How can context recall fail in RAG?", True),
        ("Why should output safety run after generation?", True),
        ("What is the weather forecast tomorrow?", False),
        ("Write a cooking recipe for dinner.", False),
        ("Summarize a football match result.", False),
        ("Plan a vacation itinerary.", False),
        ("Explain algebra homework.", False),
        ("Recommend a phone to buy.", False),
        ("Translate this marketing slogan.", False),
        ("Tell me a bedtime story.", False),
    ]
    rows = []
    correct = 0
    refused = 0
    for text, expected_allowed in tests:
        result = guard.validate_topic(text)
        predicted_allowed = bool(result["allowed"])
        correct += int(predicted_allowed == expected_allowed)
        refused += int(not predicted_allowed)
        rows.append(
            {
                "input": text,
                "expected_allowed": expected_allowed,
                "predicted_allowed": predicted_allowed,
                "correct": predicted_allowed == expected_allowed,
                "closest_topic": result["closest_topic"],
                "reason": result["reason"],
                "fallback_message": "" if predicted_allowed else guard.graceful_fallback_message(),
            }
        )
    accuracy = correct / len(tests)
    refuse_rate = refused / len(tests)
    rows.append(
        {
            "input": "SUMMARY",
            "expected_allowed": "",
            "predicted_allowed": "",
            "correct": "",
            "closest_topic": "",
            "reason": f"accuracy={accuracy:.3f}; refuse_rate={refuse_rate:.3f}; target_accuracy>=0.75",
            "fallback_message": guard.graceful_fallback_message(),
        }
    )
    pd.DataFrame(rows).to_csv(PHASE_DIR / "topic_guard_test_results.csv", index=False)
    print(f"Topic validator accuracy={accuracy:.0%} | refuse_rate={refuse_rate:.0%}")


if __name__ == "__main__":
    run_tests()
