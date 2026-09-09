# Project notes

## Why TF-IDF and logistic regression

The project is intended to be inspectable. TF-IDF creates a sparse feature for
each word or two-word phrase, and logistic regression learns one weight per
feature. Positive weights support the phishing class; negative weights support
the legitimate class. This makes the baseline easier to debug than a larger
language model.

## Why the evaluation changed

The first version randomly split messages produced by the same small set of
templates. It scored 100%, largely because near-identical patterns appeared in
training and testing. That result checked the software but said little about
generalisation.

The current version trains on all 240 generated examples and evaluates on 20
messages written separately. The challenge set deliberately includes overlap:
legitimate security notices use words such as "urgent" and "password", while
some phishing messages avoid those obvious terms.

## Reading the errors

The challenge set currently produces three false positives and four false
negatives. False positives interrupt genuine mail. False negatives expose a
user to phishing. Raising the 0.5 decision threshold will usually reduce false
positives and increase false negatives; lowering it usually does the opposite.

The most useful output is `results/predictions.csv`, because it shows which
messages failed and the model probability for each one.

## Known weak points

- The challenge set is small and was still written for this repository.
- There is no sender, URL, header or attachment information.
- Training templates use clearer label-specific language than real email.
- Probabilities are not calibrated.
- The dashboard retrains at startup rather than loading a versioned model.

## Next experiment

Freeze the current pipeline and test it on a legally reusable external corpus
without tuning on that test set. Group messages by campaign or sender, compare
word and character n-grams, and choose a threshold from the cost of each error
type rather than accuracy alone.
