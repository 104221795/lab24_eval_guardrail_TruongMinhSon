from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score


PHASE_DIR = Path(__file__).resolve().parent


def interpretation(kappa: float) -> str:
    if kappa < 0:
        return "worse than chance"
    if kappa <= 0.2:
        return "slight agreement"
    if kappa <= 0.4:
        return "fair agreement"
    if kappa <= 0.6:
        return "moderate agreement"
    if kappa <= 0.8:
        return "substantial agreement"
    return "almost perfect agreement"


def main() -> None:
    if not (PHASE_DIR / "pairwise_results.csv").exists():
        import judge_pairwise

        judge_pairwise.build_outputs()
    human = pd.read_csv(PHASE_DIR / "human_labels.csv")
    pairwise = pd.read_csv(PHASE_DIR / "pairwise_results.csv").reset_index().rename(columns={"index": "question_id"})
    merged = human.merge(pairwise[["question_id", "winner_after_swap"]], on="question_id", how="left")
    y_human = merged["human_winner"].str.upper().replace({"TIE": "tie"})
    y_judge = merged["winner_after_swap"].replace({"tie": "tie"})
    kappa = float(cohen_kappa_score(y_human, y_judge))
    text = interpretation(kappa)
    print(f"Cohen's Kappa: {kappa:.3f} ({text})")

    report_path = PHASE_DIR / "judge_bias_report.md"
    report = report_path.read_text(encoding="utf-8") if report_path.exists() else "# Judge Bias Report\n"
    if kappa < 0.6:
        root_cause = """Kappa is below 0.6, so likely causes include ambiguous rubric wording, human labels that disagree on conciseness versus completeness, judge length bias, or examples where neither answer is clearly better. The fix is to relabel disagreements, clarify rubric anchors, and add adjudicated examples to the calibration set."""
    else:
        root_cause = "Kappa is at or above 0.6, so a low-agreement root-cause investigation is not triggered for this starter run."
    addition = f"""

## Human Calibration

- Human-labeled rows: {len(merged)}
- Cohen's Kappa: {kappa:.3f}
- Interpretation: {text}
- Root-cause analysis: {root_cause}

Labels in `human_labels.csv` are starter calibration examples and should be replaced with real human review labels for production validation.
"""
    if "## Human Calibration" not in report:
        report_path.write_text(report.rstrip() + addition, encoding="utf-8")


if __name__ == "__main__":
    main()
