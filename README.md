# PhishGuard

PhishGuard is a compact phishing-email text classifier built with TF-IDF and
logistic regression. The aim is to keep the entire experiment inspectable:
how the text becomes features, how the model is trained, which messages it
gets wrong and which words influence its decisions.

The repository contains no private email and no live links. It uses generated
training messages plus a separate, manually written challenge set.

## How the experiment works

1. `data/messages.csv` supplies 240 generated training messages, balanced
   between legitimate and phishing-like text.
2. `data/challenge_messages.csv` supplies 20 harder messages written separately
   from the generator templates.
3. A scikit-learn pipeline converts subjects and bodies to TF-IDF unigram and
   bigram features.
4. Logistic regression estimates a phishing probability.
5. The runner saves message-level predictions and confusion-matrix metrics.

```text
subject + body -> TF-IDF -> logistic regression -> probability -> error review
```

## Current result

The current challenge-set result is:

| Measure | Value |
|---|---:|
| Accuracy | 65% |
| Precision | 0.67 |
| Recall | 0.60 |
| F1 | 0.63 |
| False positives | 3 |
| False negatives | 4 |

This is a more useful result than the earlier random template split, which was
too easy and produced 100%. The challenge set includes legitimate security
notices and subtler phishing messages, so shared vocabulary causes real errors.
It is still synthetic and is not a production-performance claim.

## Run it

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build_demo_dataset.py
python run_experiment.py
python -m pytest
streamlit run app.py
```

`run_experiment.py` writes `results/metrics.json` and
`results/predictions.csv`. These files are ignored by Git because they are
reproducible outputs.

## Main files

- `scripts/build_demo_dataset.py` - repeatable training-data generator
- `data/challenge_messages.csv` - fixed evaluation set
- `phishguard/data.py` - loading and validation
- `phishguard/model.py` - TF-IDF and logistic-regression pipeline
- `phishguard/evaluation.py` - metrics and confusion matrix
- `run_experiment.py` - training, evaluation and saved outputs
- `app.py` - small Streamlit demonstration

Further design notes are in [`docs/PROJECT_NOTES.md`](docs/PROJECT_NOTES.md).
The formatted report is [`docs/PhishGuard_Project_Report.pdf`](docs/PhishGuard_Project_Report.pdf).

## Limits

- Both training and challenge messages are synthetic and English-only.
- The model sees text but not sender reputation, headers, URLs or attachments.
- Twenty challenge messages are too few for a stable performance estimate.
- Word features are easy to evade with new phrasing or obfuscation.
- The probability is not calibrated for operational use.

A practical next step is external evaluation on a licensed public corpus,
split by sender or campaign, followed by threshold and calibration analysis.

## Licence

The code is released under the MIT licence. Do not upload private messages to
the demonstration dashboard.
