# Testset Review Notes

Total questions: 52

## Distribution

| evolution_type | count |
| --- | --- |
| simple | 26 |
| reasoning | 13 |
| multi_context | 13 |

## Manual Review Notes

- The test set was manually reviewed for clear wording and direct relevance to Lab 24.
- Questions are generated from the correct Day 18 corpus: BCTC.pdf and Nghị định 13/2023/NĐ-CP.
- Distribution intentionally follows 50% simple, 25% reasoning, and 25% multi-context.
- Ground-truth answers are short so RAGAS or fallback heuristics can compare them consistently.
- At least 10 questions were manually reviewed; one question was explicitly edited for scope clarity.
- Corpus manifest and derived text evidence pages are saved in `day18_corpus_manifest.json` and `day18_corpus_text_pages.md`.

## Manual Review Sample

| id | status | action | note |
| --- | --- | --- | --- |
| 1 | reviewed | kept | Clear BCTC form-number question from Day 18 test set. |
| 2 | reviewed | kept | Clear tax-period question grounded in BCTC.pdf. |
| 5 | reviewed | kept | Nghị định 13 topic question is direct and answerable. |
| 9 | reviewed | kept | Personal identifier question maps to Nghị định 13 definitions. |
| 11 | reviewed | edited | Edited wording to explicitly ask how GTGT payable is calculated from output and input VAT. |
| 17 | reviewed | kept | Negative-evidence banking question is useful for hallucination testing. |
| 22 | reviewed | kept | Simple tax document question checks source classification. |
| 31 | reviewed | kept | Reasoning question checks cross-source mismatch handling. |
| 44 | reviewed | kept | Multi-context question requires distinguishing BCTC from legal document. |
| 52 | reviewed | kept | Multi-context retrieval failure question maps to RAGAS recall. |

## Suspicious or Weak Questions

- Some cost and latency questions use estimated values because they depend on production traffic and model choice.
- Multi-context questions are synthetic but map to realistic evaluation and guardrail design decisions.