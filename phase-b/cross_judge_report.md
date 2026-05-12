# Cross-Judge Protocol Report

This bonus protocol compares each answer pair with multiple judge profiles and aggregates votes by majority.

## Judges

- `accuracy_first`: prioritizes factual match to ground truth.
- `concise_first`: prioritizes concise but still relevant answers.
- `completeness_first`: prioritizes coverage of ground-truth content.
- `gemini_optional`: live Gemini judge only when `USE_GEMINI_JUDGE=true`.

## Summary

- Questions judged: 30
- Judges used: accuracy_first, concise_first, completeness_first
- Mean agreement rate: 0.989
- Final winner counts: {'tie': 24, 'A': 6}

## Proof Artifact

- `phase-b/cross_judge_results.csv`
- `phase-b/cross_judge_summary.json`