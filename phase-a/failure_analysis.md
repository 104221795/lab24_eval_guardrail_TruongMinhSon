# Failure Cluster Analysis

## Bottom 10 Questions

| # | Question | Type | Faithfulness | Answer Relevancy | Context Precision | Context Recall | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Why should an output guard run after the RAG answer is generated? | reasoning | 0.857 | 0.75 | 0.564 | 0.6 | 0.693 |
| 2 | Why use pairwise judging? | simple | 0.813 | 0.794 | 0.56 | 0.642 | 0.702 |
| 3 | How do input guards, output guards, and audit logs reduce risk? | multi_context | 0.67 | 0.697 | 0.753 | 0.788 | 0.727 |
| 4 | What is prompt injection detection? | simple | 0.857 | 0.75 | 0.65 | 0.7 | 0.739 |
| 5 | What metric target is used for context precision? | simple | 0.857 | 0.812 | 0.575 | 0.714 | 0.739 |
| 6 | Why run adversarial tests? | simple | 0.857 | 0.75 | 0.65 | 0.7 | 0.739 |
| 7 | What is a refusal response? | simple | 0.857 | 0.75 | 0.65 | 0.7 | 0.739 |
| 8 | Why is deterministic fallback useful in this lab? | reasoning | 0.857 | 0.75 | 0.65 | 0.7 | 0.739 |
| 9 | Why should topic validation occur before RAG? | reasoning | 0.857 | 0.75 | 0.65 | 0.7 | 0.739 |
| 10 | How can manual review improve generated testsets? | multi_context | 0.857 | 0.75 | 0.65 | 0.7 | 0.739 |

## Clusters Identified

### Cluster C1: Multi-hop reasoning failures

Pattern: reasoning and multi-context questions lose answer relevancy when the answer compresses multiple requirements into a generic response.

Example questions:

- Why should an output guard run after the RAG answer is generated?
- How do input guards, output guards, and audit logs reduce risk?

Root cause: the mock retriever does not rewrite multi-step questions into topic-specific subqueries.

Proposed technical fix: add query rewriting that decomposes multi-hop questions, retrieve top_k=5 per subquery, then rerank merged candidates.

### Cluster C2: Off-topic retrieval / weak context precision

Pattern: retrieved contexts sometimes include broad evaluation text when the question asks for a narrow guardrail or CI/CD detail.

Example questions:

- Why use pairwise judging?
- Why should an output guard run after the RAG answer is generated?

Root cause: keyword-only retrieval has no metadata filter for topic or artifact type.

Proposed technical fix: use hybrid search BM25 + vector retrieval with metadata filtering by topic, then apply a cross-encoder reranker.

### Cluster C3: Low context recall

Pattern: answers that require two concepts are sometimes supported by only one retrieved chunk.

Example questions:

- Why should an output guard run after the RAG answer is generated?
- Why use pairwise judging?

Root cause: chunk selection is capped too tightly and does not enforce coverage diversity.

Proposed technical fix: tune top_k from 3 to 5, use 500-token chunks with 80-token overlap, and enforce one chunk per predicted topic.