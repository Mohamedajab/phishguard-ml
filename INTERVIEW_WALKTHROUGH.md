# PhishGuard: interview walkthrough

## Thirty-second explanation

“This is a readable phishing-text baseline using TF-IDF and logistic regression.
I compare word and character features and choose thresholds from training-only
predictions. The data is synthetic, so the useful part is the evaluation and
error analysis, not a claim that it is ready to filter email.”

Implementation and synthetic-data construction used coding-assistant support.
Be clear about that, then demonstrate understanding by running and modifying it.

## Follow the experiment

`research.py` loads the training and challenge CSVs. `phishguard/data.py` checks
columns, labels, IDs, empty text and simple overlap. Training examples are grouped
by body template. Four group folds produce out-of-fold probabilities. Thresholds
are compared on those training predictions. Word and character pipelines are
then fitted to all training messages and tested on the same fixed challenge.
The runner writes the comparison, curves, folds, thresholds and every error.

## File map

| File | What to explain |
|---|---|
| `phishguard/data.py` | Schema mapping and validation. It catches exact normalised overlap, not paraphrases. |
| `phishguard/model.py` | A Pipeline keeps TF-IDF fitting inside a training fold. Word 1-2 grams and character-within-word 3-5 grams feed balanced logistic regression. |
| `phishguard/evaluation.py` | Accuracy, precision, recall, F1 and confusion counts. |
| `scripts/build_demo_dataset.py` | Reproducible generator. Its few label-specific templates are the main weakness. |
| `data/messages.csv` | Synthetic training data, not a public email corpus. |
| `data/challenge_messages.csv` | Twenty separately constructed synthetic cases; labels can be ambiguous without sender/link evidence. |
| `research.py` | Group folds, out-of-fold predictions, threshold selection, model comparison, curves and errors. |
| `research_dashboard.py` | Reads saved results; it does not retrain or tune from the UI. |
| `tests/` | Validation, overlap, groups, models, thresholds, full runner and dashboard execution. |
| `.github/workflows/tests.yml` | Rebuilds results and tests on Linux with read-only repository permissions. |

## Concepts to explain

TF-IDF makes a sparse vector. Logistic regression combines feature values with
learned coefficients and an intercept, then applies a sigmoid. The output is a
score between zero and one, not automatically a calibrated real-world probability.

Word bigrams preserve short phrases. Character n-grams capture fragments and
some spelling variants, but can learn shortcuts too. Equal feature caps do not
make the representations equivalent. Balanced class weights do not recreate
real phishing prevalence.

ROC describes ranking across false-positive and true-positive rates. PR shows
the precision/recall trade-off and depends strongly on prevalence. AUC does not
choose an operating threshold or encode the costs of missed attacks and alarms.

## Results you should be able to derive

Word features give 6 true positives, 7 true negatives, 3 false positives and
4 false negatives: precision 6/9, recall 6/10 and F1 .6316. Character features
give 2 TP, 7 TN, 3 FP and 8 FN: F1 .2667. Both get perfect grouped training CV.
That gap shows that careful splitting cannot repair unrepresentative data.

## Likely questions

- **Was the first 100% fake?** No; it described an easy split. Presenting it as
  generalisation evidence was invalid because template variants crossed the split.
- **Why not a transformer?** A bigger model does not fix leakage or ambiguous labels.
- **Why optimise F1?** It is a declared simple objective, not a deployment cost model.
- **Is the challenge independent?** It is separate but synthetic, author-aware and
  already inspected. No external validation has happened.
- **Why did character features lose?** They represented this tiny dataset less
  usefully; the study cannot establish a general reason or universal ranking.
- **Next step?** Licensed de-identified data, campaign and time separation,
  near-duplicate checks, validation-only calibration, then one untouched test.

Before presenting, choose one false positive and one false negative from
`docs/ERROR_ANALYSIS.md`, predict the effect of raising the threshold, and add
one loader test yourself. That is a better demonstration than memorising scores.
