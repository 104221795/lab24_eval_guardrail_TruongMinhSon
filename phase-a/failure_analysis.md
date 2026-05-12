# Failure Cluster Analysis

## Bottom 10 Questions

| # | Question | Type | Faithfulness | Answer Relevancy | Context Precision | Context Recall | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Thuế GTGT phát sinh trong kỳ được tính từ những chỉ tiêu nào? | reasoning | 0.96 | 0.95 | 0.634 | 0.82 | 0.841 |
| 2 | Hàng hóa, dịch vụ bán ra chịu thuế suất 10% có giá trị và thuế GTGT là bao nhiêu? | simple | 0.96 | 0.95 | 0.657 | 0.82 | 0.847 |
| 3 | Tờ khai được lập ngày nào và người ký đại diện là ai? | reasoning | 0.84 | 0.87 | 0.762 | 0.92 | 0.848 |
| 4 | Trong hai tài liệu, tài liệu nào nói về thuế và tài liệu nào nói về dữ liệu cá nhân? | multi_context | 0.96 | 0.95 | 0.661 | 0.82 | 0.848 |
| 5 | Trong hai tài liệu, có thông tin về tên ngân hàng hoặc số tài khoản nộp thuế của CÔNG TY CỔ PHẦN DHA SURFACES không? | multi_context | 0.96 | 0.95 | 0.688 | 0.82 | 0.854 |
| 6 | Tờ khai thuế GTGT trong BCTC.pdf sử dụng mẫu số nào? | simple | 0.96 | 0.807 | 0.734 | 0.92 | 0.855 |
| 7 | Kỳ tính thuế của tờ khai thuế GTGT là thời gian nào? | simple | 0.96 | 0.807 | 0.736 | 0.92 | 0.856 |
| 8 | Nghị định 13 có nhắc đến dữ liệu cá nhân cơ bản không? | simple | 0.96 | 0.95 | 0.746 | 0.82 | 0.869 |
| 9 | Mã số thuế của người nộp thuế trong tờ khai là gì? | simple | 0.96 | 0.83 | 0.776 | 0.92 | 0.871 |
| 10 | So sánh bản chất của BCTC.pdf và Nghị định 13/2023/NĐ-CP. | multi_context | 0.96 | 0.95 | 0.76 | 0.82 | 0.872 |

## Clusters Identified

### Cluster C1: Multi-hop reasoning failures

Pattern: reasoning and multi-context questions lose answer relevancy when the answer compresses multiple requirements into a generic response.

Example questions:

- Thuế GTGT phát sinh trong kỳ được tính từ những chỉ tiêu nào?
- Tờ khai được lập ngày nào và người ký đại diện là ai?

Root cause: the mock retriever does not rewrite multi-step questions into topic-specific subqueries.

Proposed technical fix: add query rewriting that decomposes multi-hop questions, retrieve top_k=5 per subquery, then rerank merged candidates.

### Cluster C2: Off-topic retrieval / weak context precision

Pattern: retrieved contexts sometimes include broad evaluation text when the question asks for a narrow guardrail or CI/CD detail.

Example questions:

- Thuế GTGT phát sinh trong kỳ được tính từ những chỉ tiêu nào?
- Hàng hóa, dịch vụ bán ra chịu thuế suất 10% có giá trị và thuế GTGT là bao nhiêu?

Root cause: keyword-only retrieval has no metadata filter for topic or artifact type.

Proposed technical fix: use hybrid search BM25 + vector retrieval with metadata filtering by topic, then apply a cross-encoder reranker.

### Cluster C3: Low context recall

Pattern: answers that require two concepts are sometimes supported by only one retrieved chunk.

Example questions:

- Thuế GTGT phát sinh trong kỳ được tính từ những chỉ tiêu nào?
- Hàng hóa, dịch vụ bán ra chịu thuế suất 10% có giá trị và thuế GTGT là bao nhiêu?

Root cause: chunk selection is capped too tightly and does not enforce coverage diversity.

Proposed technical fix: tune top_k from 3 to 5, use 500-token chunks with 80-token overlap, and enforce one chunk per predicted topic.