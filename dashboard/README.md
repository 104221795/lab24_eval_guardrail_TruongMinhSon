# Eval Dashboard Bonus

This optional Streamlit dashboard visualizes the generated Lab 24 artifacts:

- Phase A RAGAS metrics and bottom-10 failures
- Phase B cross-judge protocol results
- Phase C PII, adversarial, output guard, and latency tests
- Day 18 corpus manifest

## Run

```powershell
cd D:\MyNewDesktop\lab24_guardrails_starter\lab24-eval-guardrails
pip install -r requirements-dashboard.txt
streamlit run dashboard/app.py
```

Proof artifact: `dashboard/app.py` plus generated CSV/JSON files.
