# PhishGuard interview guide

## The 30-second explanation

PhishGuard is a reproducible text-classification experiment. It combines an
email subject and body, converts the text to TF-IDF word and phrase features,
and uses logistic regression to estimate a phishing probability. I chose a
linear model because I can inspect the learned terms and explain the full
pipeline. The included data is synthetic, so the score demonstrates that the
implementation works; it does not prove real-world accuracy.

## File-by-file walkthrough

- `scripts/build_demo_dataset.py` creates balanced, harmless examples with a
  fixed random seed.
- `phishguard/data.py` validates the CSV and combines subject and body.
- `phishguard/model.py` defines TF-IDF, logistic regression and feature-weight
  inspection.
- `phishguard/evaluation.py` calculates the scores and confusion matrix.
- `run_experiment.py` makes the train/test split, fits the pipeline and records
  results.
- `app.py` provides a Streamlit demonstration and shows influential terms.
- `tests/` checks validation, metric arithmetic and model output.

## Ideas to understand

### TF-IDF

Term frequency measures how often a term appears in a message. Inverse document
frequency reduces the weight of terms that appear in many messages. Their
product creates a numeric feature for each word or two-word phrase.

### Logistic regression

The classifier forms a weighted sum of the TF-IDF features and converts it to a
probability. Its decision boundary is linear. This is simple, fast and
inspectable, although it cannot understand language in the way a larger model
can.

### Data leakage and generalisation

The demonstration split is reproducible and stratified, but messages generated
from related templates appear on both sides. A stronger evaluation would keep
whole campaigns or senders out of training and test on an external dataset.

## Questions I should be ready to answer

1. Why is recall particularly important for a phishing detector?
2. Why can high test accuracy on synthetic data be misleading?
3. What information does the confusion matrix add beyond accuracy?
4. Why use a pipeline instead of fitting TF-IDF and the classifier separately?
5. How would character n-grams help with misspelled or obfuscated words?
6. What would change before using this with real email?

## Small exercises

1. Change the probability threshold in `app.py` from 0.5 to 0.7 and explain
   which error type is likely to increase.
2. Change `ngram_range` in `phishguard/model.py` to `(1, 1)`, rerun the
   experiment, and compare the terms and metrics.
3. Add one difficult legitimate message containing the word "urgent" and see
   whether the model still classifies it correctly.

