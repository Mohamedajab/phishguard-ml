# PhishGuard

An inspectable phishing-text experiment: TF-IDF, logistic regression,
training-only threshold selection and error review. It compares word and
character n-grams without hiding the weaknesses of its synthetic data.

**Status:** 240 generated training messages and 20 AI-assisted synthetic
challenge messages. No external corpus evaluated. Educational work, not an
operational email filter.

## Run locally (Python 3.11+)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python research.py
python -m pytest
streamlit run research_dashboard.py
```

On Linux/macOS use `source .venv/bin/activate`. `run_experiment.py` and `app.py`
retain the simpler word-feature demo. Training data is reproducible with
`python scripts/build_demo_dataset.py` (seed 42).

## Experiment

Keep body-template groups together in four training folds. Fit TF-IDF within
each fold. Select thresholds using training out-of-fold predictions, then fit
on all training data and evaluate the fixed challenge. Save folds, curves,
thresholds and individual errors.

| Representation | Training CV F1 | Challenge F1 | Challenge ROC AUC |
|---|---:|---:|---:|
| Word 1-2 grams | 1.00 | .632 | .70 |
| Character 3-5 grams | 1.00 | .267 | .41 |

Both selected threshold 0.5. Perfect CV remains a warning: subject templates
and label-specific language still recur. The earlier random-split 100% was not
valid generalisation evidence. Twenty synthetic challenge messages are also
too few for a deployment claim. Character features did not improve this run.

## Outputs and external data

`results/research/` contains `research.json`, `folds.csv`, `thresholds.csv`,
`curves.csv` and `predictions.csv`. Generated results are ignored by Git.
Re-running replaces these files; use `--output` to retain separate experiments.

```powershell
python research.py --training external/train.csv --challenge external/test.csv --schema mapping.json --output results/external-run
```

Canonical columns: `message_id`, `subject`, `body`, `label`; external training
also requires `group` (campaign/sender, not row ID). Optional schema JSON:
`{"column_map":{"message":"body","target":"label"},"label_map":{"ham":0,"spam":1}}`.
Both files must use the same mapping. Normalised text overlap and shared
explicit groups are rejected. Near-duplicate/time leakage need further checks.
Record source/licence and keep private messages outside the repository.

## Start reading

- [Interview walkthrough](INTERVIEW_WALKTHROUGH.md): concepts, files and questions.
- [Research audit](docs/RESEARCH_AUDIT.md): leakage, protocol and limitations.
- [Error review](docs/ERROR_ANALYSIS.md) and [verification record](docs/VERIFICATION.md).
- [Printable report](docs/PhishGuard_Project_Report.pdf).
- `phishguard/`: loader, pipelines and metrics.
- `research.py`: grouped evaluation and saved evidence.
- `tests/`: loading, overlap, grouping, models, metrics and dashboards.

Scores are uncalibrated. Sender identity, attachments and URL reputation are
outside scope. MIT licence retained.
