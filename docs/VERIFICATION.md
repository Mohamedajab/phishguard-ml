# Verification record

Local check: 10 September 2026, Python 3.14 on Windows.
Twelve tests passed, including the research runner and Streamlit dashboard.
Statement coverage: 88% across `phishguard` and `research.py` (137 statements).
This is not branch coverage or proof that every failure mode is tested.

```text
python -m pip install -r requirements-dev.txt
python research.py
python -m coverage run --source=phishguard,research -m pytest
python -m coverage report -m
```

Tested versions: NumPy 2.5.2, pandas 2.3.3, scikit-learn 1.9.0,
Streamlit 1.63.0, Altair 6.2.2, pytest 8.4.2 and coverage 7.16.0.
Supported ranges are not an exact environment lock.

Tracked text was checked for common OpenRouter/GitHub token and private-key
patterns with no match. This is a bounded pattern check, not a comprehensive
secret audit. External datasets must remain outside the repository.
