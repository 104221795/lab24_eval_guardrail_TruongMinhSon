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
- Distribution intentionally follows 50% simple, 25% reasoning, and 25% multi-context.
- Ground-truth answers are short so RAGAS or fallback heuristics can compare them consistently.
- At least 10 questions were manually reviewed; one question was explicitly edited for scope clarity.

## Manual Review Sample

| id | status | action | note |
| --- | --- | --- | --- |
| 1 | reviewed | kept | Clear single-hop faithfulness question. |
| 2 | reviewed | kept | Clear answer relevancy question. |
| 5 | reviewed | kept | Guardrail-stack wording is in scope. |
| 9 | reviewed | kept | Kappa question maps to calibration. |
| 11 | reviewed | edited | Edited from 'What is CI/CD?' to focus on evaluation gates. |
| 17 | reviewed | kept | Threshold question has explicit expected value. |
| 27 | reviewed | kept | Reasoning question checks metric interaction. |
| 30 | reviewed | kept | Reasoning question checks top_k tradeoff. |
| 40 | reviewed | kept | Multi-context question links metrics and CI/CD. |
| 52 | reviewed | kept | False-positive tradeoff question is clear. |

## Suspicious or Weak Questions

- Some cost and latency questions use estimated values because they depend on production traffic and model choice.
- Multi-context questions are synthetic but map to realistic evaluation and guardrail design decisions.