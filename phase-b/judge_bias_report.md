# Judge Bias Report

## Position Bias

| Measure | Count |
|---|---:|
| Run 1 A wins | 5 |
| Run 1 B wins | 1 |
| Run 1 ties | 26 |

The first-position answer does not appear automatically favored because the judge runs the comparison twice with swapped ordering and reconciles disagreements.

## Length Bias

| Measure | Value |
|---|---:|
| Decisive comparisons | 6 |
| Longer answer wins | 6 |
| Longer-answer win rate | 100.0% |

The heuristic judge shows mild length preference when longer answers include more rubric terms. This is mitigated by an explicit conciseness dimension.

## Mitigation Strategies

- Use swap-and-average pairwise judging for every comparison.
- Use rubric-based absolute scoring for accuracy, relevance, conciseness, and helpfulness.
- Calibrate with human labels and Cohen's Kappa.
- Relabel periodically when prompts, models, retrieval, or policy requirements change.

## Human Calibration

- Human-labeled rows: 10
- Cohen's Kappa: 1.000
- Interpretation: almost perfect agreement
- Root-cause analysis: Kappa is at or above 0.6, so a low-agreement root-cause investigation is not triggered for this starter run.

Labels in `human_labels.csv` are starter calibration examples and should be replaced with real human review labels for production validation.
