# PhishGuard

An inspectable phishing-text experiment using TF-IDF and logistic regression.
It compares word and character features, selects a decision threshold from
training-only predictions, and keeps message-level errors visible.

Status: 240 generated training messages and 20 AI-assisted synthetic challenge
messages. No external corpus has been evaluated, so this is educational work,
not an operational email filter.

## Run it

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python research.py
python -m pytest
streamlit run research_dashboard.py
```

Use `source .venv/bin/activate` on Linux or macOS. Regenerate the training CSV
with `python scripts/build_demo_dataset.py` (fixed seed 42).

## Experiment and results

Four folds keep examples from the same body template together. TF-IDF is fitted
inside every fold. Thresholds are selected from out-of-fold training predictions,
then each representation is fitted on all training data and evaluated once on
the fixed challenge.

| Representation | Training CV F1 | Challenge F1 | Challenge ROC AUC |
|---|---:|---:|---:|
| Word 1-2 grams | 1.00 | .632 | .70 |
| Character 3-5 grams | 1.00 | .267 | .41 |

Both selected threshold 0.5. Perfect training CV is a warning rather than a
headline: subject templates and label-specific language still recur. The first
random-split 100% result was not valid evidence of generalisation. Twenty
synthetic challenge messages are also too few for a deployment claim.

`results/research/` contains the local generated outputs: fold predictions,
threshold table, ROC/PR coordinates and per-message errors. These files are
ignored by Git and can be rebuilt.

## External data

```powershell
python research.py --training external/train.csv --challenge external/test.csv --schema mapping.json --output results/external-run
```

Canonical columns are `message_id`, `subject`, `body`, `label`, plus a training
`group` such as campaign or sender. Optional schema JSON maps source columns and
labels. Both files must use the same mapping. Exact normalised text overlap and
shared explicit groups are rejected; semantic duplicates and time leakage still
need dataset-specific checks. Record the corpus source/licence and keep private
mail outside the repository.

## Start reading

- [Interview walkthrough](INTERVIEW_WALKTHROUGH.md): concepts and file map.
- [Research audit](docs/RESEARCH_AUDIT.md): leakage and remaining limitations.
- [Error analysis](docs/ERROR_ANALYSIS.md): seven word-model challenge errors.
- [Verification](docs/VERIFICATION.md): tests, coverage and environment.
- `research.py`: grouped evaluation and saved evidence.
- `phishguard/`: loading, feature pipelines and metrics.

Scores are uncalibrated. Sender identity, attachments, link reputation and
transport headers are outside scope. MIT licence retained.
