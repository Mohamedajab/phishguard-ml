# Dataset and evaluation guide: PhishGuard

PhishGuard is an educational **text-only** phishing classification study.
It learns from labelled synthetic email subjects/bodies and compares word
and character TF-IDF pipelines with logistic regression. There has been
**no evaluation on an independently collected real email corpus**.
Do not use its outputs to block mail or make security decisions.

## Inputs and labels

`phishguard/data.py` expects two CSV files, one for training and one for
a *fixed* challenge evaluation. The canonical columns are:

| Column | Required | Meaning |
| --- | --- | --- |
| `message_id` | Yes | Non-null unique identifier *within each file* |
| `subject` | Yes | Email subject (blank text is allowed if body is non-empty) |
| `body` | Yes | Email body (blank text is allowed if subject is non-empty) |
| `label` | Yes | Binary 0 = legitimate, 1 = phishing; both values must occur in each file |
| `group` | Required for external training | Campaign, sender, collection source or similar leakage boundary |

The model input is the stripped **subject + space + body**. It has no
sender identity, headers, linked-page content, attachment analysis or
reputation service. In an external dataset, choose `group` to reflect a
realistic generalisation boundary, not arbitrary row IDs.

When a `group` column exists in both files, the loader rejects shared
group values. It also rejects exact case-folded, whitespace-normalised
train/challenge text overlaps. **Paraphrases, near-duplicates and time-based
leakage are not automatically detected.** Blank group values are not a
substitute for a real source grouping policy.

For third-party data, create `mapping.json` if needed:

```json
{
  "column_map": {
    "email_identifier": "message_id",
    "email_subject": "subject",
    "email_body": "body",
    "class_name": "label",
    "campaign_id": "group"
  },
  "label_map": {
    "legitimate": 0,
    "phishing": 1
  }
}
```

`column_map` maps **source** names to canonical names. Apply the same
mappings to both input files. The JSON above is a schema example, not
a claim that any particular external CSV exists.

## Run the built-in experiment

```bash
python -m venv .venv
# Activate the environment for your shell.
python -m pip install -r requirements-dev.txt
python -m pytest
python research.py
streamlit run research_dashboard.py
```

The defaults are `data/messages.csv` (240 generated training messages),
`data/challenge_messages.csv` (20 AI-assisted synthetic challenge
messages) and `results/research/`. The fixed-seed training generator is
`python scripts/build_demo_dataset.py`.

For your own licensed, de-identified dataset:

```bash
python research.py --training external/train.csv --challenge external/test.csv --schema mapping.json --output results/external-run
```

Keep real private mail, protected attributes and credentials out of Git.
Record corpus provenance, date, licence, annotation process, group definition
and exact train/evaluation separation outside the raw model scores.

## Leakage-aware model selection

`research.py` uses `StratifiedGroupKFold` with **four folds**, shuffle
enabled and seed 42. Synthetic body-template groups keep variants of
each body template in one fold. For each of the two feature representations:

1. A fresh TF-IDF + logistic regression pipeline fits *inside each fold*.
2. Out-of-fold predictions are saved for all training messages.
3. Candidate thresholds **0.10 through 0.90, step 0.05** are scored
   against the training OOF labels using F1; ties favour closeness to 0.5.
4. The representation is selected using *mean fold F1 at threshold 0.5*,
   with the word representation winning a tie by iteration order.
5. Each representation fits once on all training data and is scored
   once against the fixed challenge. Challenge labels are not used
   during threshold or representation selection.

Threshold optimisation is **not nested cross-validation**: the OOF scores
serve model-selection purposes and are not an unbiased final estimate.
Body-template grouping also does not remove recurring subject templates,
shared label language or every possible source shortcut.

## Inspectable outputs

| Artifact in `--output` directory | What it contains |
| --- | --- |
| `research.json` | Chosen representation, thresholds, model scores, input hashes, seed and package versions |
| `folds.csv` | Per-training-message out-of-fold probabilities and groups |
| `thresholds.csv` | Training OOF metrics for all candidate thresholds |
| `predictions.csv` | Challenge text, actual label, predicted label, probability and error category for each representation |
| `curves.csv` | ROC and precision/recall curve coordinates |

Use the per-message errors before drawing conclusions from a scalar metric.
The output directory is not a blinded publication dataset, and
`results/research/` is generated locally rather than the frozen source.

## What current results mean

| Model | Training CV F1 | Synthetic challenge F1 | Challenge ROC AUC |
| --- | ---: | ---: | ---: |
| Word 1–2 grams | 1.00 | 0.632 | 0.70 |
| Character 3–5 grams | 1.00 | 0.267 | 0.41 |

The training scores are **not** evidence of real-world performance.
On the challenge, `docs/ERROR_ANALYSIS.md` reviews seven word-model
errors, including legitimate security notices called phishing and phishing
messages without common urgency/password terms.

The `predict_proba` values have **not** been independently calibrated to
real phishing prevalence. A reported score of 0.8 is not an established
80% real-world probability. Threshold 0.5 is the observed OOF-selected
value for both models, not a prescribed operational security threshold.

## Minimum protocol for a future external evaluation

- Obtain a lawful, licensed and appropriately de-identified corpus.
- Keep campaigns/senders and time periods separated where the deployment
  question requires it, including *semantic* and exact-overlap checks.
- Freeze feature, threshold and selection rules before viewing final labels.
- Report class prevalence, uncertainty and false-positive/false-negative
  costs; consider precision/recall under operational base rates.
- Investigate mismatches with independent labels and source evidence.
- Compare against simple baselines before considering deployment.

See [research audit](RESEARCH_AUDIT.md) for the full list of limitations.

