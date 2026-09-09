# Challenge error review

These are interpretations of synthetic text, not verified causes of model decisions.
The word model uses threshold 0.5 selected from training OOF predictions.

| ID | Error | Score | What the text illustrates |
|---|---|---:|---|
| challenge-legit-03 | False positive | .559 | University security alert asks users to use their normal portal. Security vocabulary overlaps phishing wording. |
| challenge-legit-06 | False positive | .556 | Planned mailbox migration mentions sign-in but explicitly says IT will not ask for a password. Bag-of-ngrams does not reliably represent negation/context. |
| challenge-legit-07 | False positive | .556 | Refund already processed, no new bank details requested. Vocabulary alone does not distinguish reassurance from a demand. |
| challenge-phish-03 | False negative | .447 | Participation payment directs the reader to an account form. The text lacks an explicit password request. |
| challenge-phish-04 | False negative | .426 | Library restrictions create pressure to follow attached instructions, without typical account-verification language. |
| challenge-phish-05 | False negative | .468 | Conference booking directs users to a replacement form. Plausible context masks the supposed malicious intent. |
| challenge-phish-07 | False negative | .309 | Voicemail pretext redirects to a viewer; without inspecting that destination the label is especially hard to justify from text alone. |

The character model misses eight of ten phishing-labelled examples and flags
three benign ones. Its challenge F1 is .267 versus .632 for words, despite
perfect CV for both. See the complete per-model comparison in the generated
`results/research/predictions.csv`.

Do not claim that word coefficients establish why any one error occurred.
Review actual feature contributions or controlled edits to test those hypotheses.
For a real corpus, validate labels using sender/link/conversation evidence and
independent annotation before using them as ground truth.
