# PhishGuard: interview walkthrough

## A short introduction

“This is a readable phishing-text baseline using TF-IDF and logistic regression.
I compare word and character features and choose thresholds from training-only
predictions. The data is synthetic, so it demonstrates evaluation and error
analysis rather than a deployable phishing filter.”

Implementation and challenge construction used AI assistance. Be clear about
that, and practise explaining and modifying the code instead of memorising scores.

## Important files

| File | Purpose and decision |
|---|---|
| `phishguard/data.py` | External schema mapping, ID/text/label validation, subject/body combination, normalised overlap and group checks. Not a semantic deduplicator. |
| `phishguard/model.py` | Pipeline fits TF-IDF within each fold. Word 1-2 grams or character-within-word 3-5 grams feed balanced logistic regression. Coefficients are associations, not causes. |
| `phishguard/evaluation.py` | Accuracy, precision, recall, F1 and confusion counts. Handles zero predicted positives with precision zero. |
| `phishguard/__init__.py` | Marks the Python package. |
| `scripts/build_demo_dataset.py` | Generates 240 messages with fixed seed; its few label-specific templates are the central methodological weakness. |
| `data/messages.csv` | Synthetic training data, not a public email corpus. |
| `data/challenge_messages.csv` | Twenty separately constructed synthetic examples, previously inspected; ambiguous without real sender context. |
| `run_experiment.py` | Simple fixed word-model example at threshold 0.5. |
| `research.py` | Body-template/external groups, four folds, saved OOF predictions, thresholds, both models, curves and errors. |
| `app.py` | Interactive demo that retrains at startup and uses threshold 0.5. |
| `research_dashboard.py` | Reads saved research outputs; ROC/PR, thresholds, comparison and errors. |
| `tests/` | Validation, overlap, groups, model options, metrics, threshold ties and Streamlit execution. |
| `.github/workflows/tests.yml` | Offline tests and experiment, no private data/credentials. |
| `requirements.txt`, `pyproject.toml`, `.gitignore` | Dependencies, test settings and exclusions. An ignore rule is not a privacy guarantee. |
| `LICENSE`, `README.md`, `docs/` | MIT permission, quick start and methodology. |

## Explain the model

TF-IDF makes a sparse vector for each message. Features get more weight when
important to that message and less common across training messages. Logistic
regression combines features with learned coefficients and an intercept, then
applies a sigmoid. The score is between zero and one, but is not automatically
a calibrated real-world probability.

Word bigrams preserve short phrases. Character n-grams capture word fragments
and some spelling variants, but can learn shortcuts too. Equal feature caps
do not mean equal information capacity. Balanced class weights alter fitting;
they do not reproduce realistic phishing prevalence.

## Explain the evaluation

Four folds keep variants of one body template together. Fit on three folds and
predict the fourth until every training message has an out-of-fold score.
Threshold selection uses those scores, never challenge labels. Word wins the
representation tie at mean training-fold F1=1.0. Both thresholds are 0.5.
The selection score is optimistic; nested CV would assess the selection process.

ROC plots true-positive against false-positive rate. PR plots precision against
recall and depends on prevalence. AUC measures ranking, not the cost of a chosen
threshold. Raising a fixed-score threshold cannot increase positive predictions
or recall, but precision need not improve monotonically on a finite sample.

## Actual findings

Word: 6 TP, 7 TN, 3 FP and 4 FN on the challenge. Precision=6/9, recall=6/10,
F1=.6316. Character: 2 TP, 7 TN, 3 FP and 8 FN; F1=.2667. Both have perfect
training CV. Validation machinery cannot repair unrepresentative data: subject
templates still recur and label-specific vocabulary remains easy.

## Questions to prepare for

- **Was the first 100% fabricated?** It described an easy random template split;
  treating it as generalisation evidence was invalid. This does not prove test
  labels entered vectoriser fitting.
- **Why not a transformer?** A larger model would not fix leakage or ambiguous labels.
- **Why F1?** A declared simple objective, not a deployment cost model. Real use
  requires acceptable false-alarm and missed-attack costs.
- **Is the challenge independent?** Separate from templates, but synthetic,
  author-aware and previously inspected. External validation is still absent.
- **Why did characters lose?** Possibly less useful representation for these
  messages; the small sample cannot establish a general causal explanation.
- **What next?** Licensed de-identified data; campaign/time splits, near-duplicate
  checks, validation-only calibration, then one untouched external evaluation.

## Practise

Open the saved errors; choose one FP and one FN and explain their vocabulary
and missing context. Predict a threshold change before reading the curve.
Add a duplicate-ID loader test. Explain why fitting TF-IDF before CV would
leak vocabulary statistics even without explicitly using the labels.
