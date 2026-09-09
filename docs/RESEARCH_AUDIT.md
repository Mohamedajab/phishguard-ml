# Research audit

The question is whether simple text features distinguish phishing-like language
from legitimate messages under a distribution change. This is AI-assisted,
synthetic educational work, not a deployed detector.

## Why the first 100% result was not valid evidence of generalisation

The original random split put variants of the same small set of templates on
both sides. Names and invoice numbers changed, but wording strongly predicted
the label. The score could correctly describe that split while being invalid
as a real-world performance claim. This is template leakage/dependence and a
dataset shortcut, not proof that the code fitted the vectoriser on test labels.
The current pipeline fits TF-IDF inside each training fold.

## Current design

`research.py` groups the 240 training messages by their 16 body templates and
uses four stratified group folds. Both word (1-2 gram) and character-within-word
(3-5 gram) pipelines use the same splits and a 3,000-feature cap. Each fold fits
its own TF-IDF vocabulary and logistic regression. Fold predictions are saved.

Thresholds 0.10 to 0.90, step 0.05, are compared using training out-of-fold F1.
Ties prefer the threshold nearest 0.5. Representation selection uses mean
training-fold F1 at 0.5, with word features winning ties. Neither selection
reads challenge labels. These are selection scores, not nested-CV estimates.

Then each representation is fitted on all training messages and evaluated on
20 fixed synthetic challenge messages. Saved ROC/PR coordinates, AUC, average
precision and message-level errors make the comparison inspectable. The
challenge was previously inspected and is not a new blind external test.

## Actual results and interpretation

Both representations obtain F1=1.00 in every training fold. Grouping bodies
does not remove recurring subject templates or all language shortcuts.
Do not advertise the CV score as realistic accuracy.

On the challenge, word features: accuracy .65, F1 .6316, ROC AUC .70;
character features: accuracy .45, F1 .2667, ROC AUC .41. Both selected threshold
0.5. Character features are not automatically better: they fragment words into
patterns and can still learn synthetic shortcuts. This comparison does not
establish superiority across corpora or hyperparameters.

## Error review

`results/research/predictions.csv` contains full synthetic text, scores, labels
and false-positive/false-negative categories for both models. Inspect messages
side by side; coefficients describe association, not causal explanations.
Legitimate security notices share phishing vocabulary, while indirect requests
may lack urgent/password wording. These are hypotheses to check against each
message, not verified causes of every error. Labels themselves can be ambiguous
without sender identity, links, headers or conversation context.

## Remaining risks

- No external, time-separated or campaign-disjoint test has been run.
- Only 20 balanced challenge messages: unstable estimates and unrealistic prevalence.
- Body groups still share subject templates. Fully grouping both can connect most
  examples into a few groups; a newly collected dataset is preferable.
- Threshold maximises F1, not a specified cost of false alarms/missed attacks.
- Scores are uncalibrated; a value of .8 is not an established 80% real-world risk.
- Only text is modelled; URLs, attachments, sender reputation and transport are absent.
- Duplicate normalised train/test text and shared explicit groups are rejected;
  semantic near-duplicates and time leakage still need dataset-specific checks.
- Dependency ranges permit version drift; run records include local versions.

## External data contract

Supply licensed, de-identified CSV files with `message_id`, `subject`, `body`,
binary `label` (0 legitimate, 1 phishing), and training `group` (campaign/sender).
Supply group in both files to check group overlap. `--schema mapping.json`
accepts `column_map` (source name to canonical name) and `label_map` (source
labels to 0/1), applied to both files. Mixed schemas should be normalised first.
Do not use row IDs as groups. Record source, licence, collection dates, label
procedure and group rationale before comparing results. No corpus is downloaded
or uploaded by the loader.

References: [scikit-learn cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)
and [data leakage guidance](https://scikit-learn.org/stable/common_pitfalls.html).
