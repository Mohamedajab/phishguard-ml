# Verification record

Local check: 9 September 2026, Python 3.14 on Windows.
Fourteen tests passed, including both Streamlit scripts with generated data.
Statement coverage: 88% across `phishguard` and `research.py` (137 statements).
This is not branch coverage or a claim that every failure mode is tested.

Run it yourself:

```text
python -m pip install -r requirements-dev.txt
python research.py
python -m coverage run --source=phishguard,research -m pytest
python -m coverage report -m
```

If Windows' global pytest temporary directory has inaccessible files, use a
new local `--basetemp .pytest_tmp/my-check` directory when invoking pytest.

Tested versions: NumPy 2.5.2, pandas 2.3.3, scikit-learn 1.9.0,
Streamlit 1.63.0, Altair 6.2.2, pytest 8.4.2, coverage 7.16.0.
The supported dependency ranges are not an exact environment lock.

Tracked text was scanned for common OpenRouter/GitHub token and private-key
patterns: no match found. This is a bounded pattern check, not a comprehensive
secret audit. Generated external data must remain outside the repository.
