# Revised classifier and comparison with Assignment 9

The Assignment 9 classifier was retrained on the same 30 messages. Sixteen of those messages appear in the Module 10 form. Three of them take the form's majority label. The other fourteen keep `expand_other`. The vectorizer, logistic regression, hyperparameters, metric definitions, and the ten 20/10 splits are the ones in `Module_9_assignment/baseline_classifier.ipynb`.

A rerun of that baseline in this environment (scikit-learn 1.5.0, NumPy 2.4.4) matches the saved Assignment 9 tables, which were produced with scikit-learn 1.9.1. No modeling change was required for the numbers to agree.

The one procedural addition is that training labels and test reference labels are separate arrays. Assignment 9 used one array for both. Separating them is what makes it possible to tell a retrained model from a rewritten test key. When both arrays are `expand_other`, the run is the Assignment 9 baseline.

## Labels that changed

Matches are the same visitor statement after names and placeholders are ignored. The map is checked in `retrain_classifier.py` and listed in `outputs/label_changes.csv`.

| Assignment 9 id | Module 10 id | Votes | `expand_other` | Majority label |
| --- | --- | --- | --- | --- |
| V16 | V15 | buyer, realtor network, buyer, renter | renter | buyer |
| V22 | V9 | buyer, buyer, other, buyer | other | buyer |
| V27 | V19 | other, media outreach, buyer, other | media outreach | other |

V16 asks for historical rental rates on a Reunion house. The majority is 2–1–1. V22 says the writer is moving to the Celebration / Windermere / Winter Garden area this spring. The majority is 3–1. V27 asks how blue-green algae affects air quality in Clermont. The majority is 2–1–1.

The other 13 matched messages have the same majority label as `expand_other`. These Assignment 9 messages were not on the form, so their labels stay: V2, V4, V5, V10, V12, V13, V14, V15, V18, V19, V24, V25, V26, V29.

Fourteen form messages are not in the Assignment 9 file (Module 10 V6, V10, V11, V14, V16, V17, V20, V22, V25, V26, V27, V28, V29, V30). They were left out so the training and test ids could stay on the Assignment 9 splits. Module 10 V11 and V27 are 2–2 ties marked adjudicated. Their stored final labels were not used.

On the 30 messages used for training, the class counts move from buyer 19, seller 1, renter 3, media outreach 2, realtor network 1, other 4 to buyer 21, seller 1, renter 2, media outreach 1, realtor network 1, other 4.

## How the scores are defined

Same rules as Assignment 9:

- Precision, recall, and specificity are one-vs-rest counts on that repeat's 10 test messages. A denominator of zero is N/A.
- F1 is N/A when precision or recall is N/A. F1 is 0 when both are 0.
- One-vs-rest AUC uses the class probability. AUC is N/A when the test set has none of that class or is entirely that class. A class missing from training gets probability 0 on every test row.
- A per-class mean skips N/A repeats. `defined_runs` is how many of the 10 repeats produced a number.
- Macro precision, recall, F1, specificity, and AUC are the unweighted mean of the classes that are defined on that repeat. The tables below then average those 10 macro scores.
- The confusion matrix pools all 10 test sets (100 rows). Messages repeat across splits, so this is 100 predictions, not 100 distinct messages.
- Seller, realtor network, and (after the revision) media outreach have a single message. Whenever that message is in the test set it is absent from training, every test row gets probability 0, and the AUC is 0.5. That 0.5 is the constant score from a missing class, not a fitted ranking.

## Four runs

Both models are scored on the same held-out ids. Test rows are never fit.

| Run | Training labels | Test reference |
| --- | --- | --- |
| Baseline, original reference | `expand_other` | `expand_other` |
| Revised model, original reference | revised labels | `expand_other` |
| Baseline model, revised reference | `expand_other` | revised labels |
| Revised model, revised reference | revised labels | revised labels |

The second run is the retraining effect. The third run is the effect of rewriting the test labels while the classifier stays the Assignment 9 model. The fourth run is the retrained classifier scored on the revised key.

## Performance of the retrained classifier

Means across the 10 repeats. Per-class precision and F1 are N/A for seller, renter, media outreach, and realtor network because the model never predicts them.

Scored on the original test labels (same key as Assignment 9):

| Class | Precision | Recall | F1 | Specificity | AUC |
| --- | --- | --- | --- | --- | --- |
| buyer | 0.583 | 1.000 | 0.731 | 0.090 | 0.713 |
| seller | N/A | 0.000 | N/A | 1.000 | 0.500 |
| renter | N/A | 0.000 | N/A | 1.000 | 0.760 |
| media outreach | N/A | 0.000 | N/A | 1.000 | 0.452 |
| realtor network | N/A | 0.000 | N/A | 1.000 | 0.500 |
| other | 0.000 | 0.000 | 0.000 | 0.954 | 0.737 |
| Macro (mean of repeats) | 0.467 | 0.238 | 0.621 | 0.841 | 0.649 |

Accuracy is 0.560. Seller recall is defined on 6 repeats, realtor network recall on 2, media outreach recall on 7, other precision on 4 and other F1 on 3. Macro F1 averages 1.3 classes per repeat.

Scored on the revised test labels:

| Class | Precision | Recall | F1 | Specificity | AUC |
| --- | --- | --- | --- | --- | --- |
| buyer | 0.667 | 1.000 | 0.798 | 0.103 | 0.743 |
| seller | N/A | 0.000 | N/A | 1.000 | 0.500 |
| renter | N/A | 0.000 | N/A | 1.000 | 0.728 |
| media outreach | N/A | 0.000 | N/A | 1.000 | 0.500 |
| realtor network | N/A | 0.000 | N/A | 1.000 | 0.500 |
| other | 0.000 | 0.000 | 0.000 | 0.954 | 0.620 |
| Macro (mean of repeats) | 0.533 | 0.257 | 0.678 | 0.843 | 0.642 |

Accuracy is 0.640. Media outreach AUC is 0.500 on all 5 repeats where the class appears in the test set, because V21 is then the only media-outreach message and it is held out, so the class has no training row.

## Side-by-side comparison

Mean of the 10 repeat scores:

| Metric | Baseline, original labels | Revised model, original labels | Baseline model, revised labels | Revised model, revised labels |
| --- | --- | --- | --- | --- |
| Accuracy | 0.550 | 0.560 | 0.630 | 0.640 |
| Macro precision | 0.434 | 0.467 | 0.501 | 0.533 |
| Macro recall | 0.235 | 0.238 | 0.253 | 0.257 |
| Macro F1 | 0.579 | 0.621 | 0.636 | 0.678 |
| Macro specificity | 0.839 | 0.841 | 0.841 | 0.843 |
| Macro AUC | 0.631 | 0.649 | 0.639 | 0.642 |

From the baseline to the revised model, with the test key held at `expand_other`: accuracy +0.010, macro precision +0.032, macro recall +0.003, macro F1 +0.042, macro specificity +0.002, macro AUC +0.017.

From the original test key to the revised test key, with the Assignment 9 model held fixed: accuracy +0.080, macro precision +0.067, macro recall +0.018, macro F1 +0.057, macro specificity +0.002, macro AUC +0.008.

The two shifts add. The full gap from the Assignment 9 baseline to the revised model on the revised key is accuracy +0.090. Of that, +0.080 is the new test labels and +0.010 is the retrained model.

Macro F1 still drops any class the model does not predict. The retrained model predicts `other` on fewer repeats, so the number of classes inside macro F1 falls from 1.4 to 1.3. Part of the macro F1 rise is that `other`'s F1 of 0 leaves the average.

### Per class, original test labels

This column pair holds the test key fixed, so the change is retraining.

| Class | Baseline P / R / F1 | Revised P / R / F1 | Baseline specificity / AUC | Revised specificity / AUC |
| --- | --- | --- | --- | --- |
| buyer | 0.579 / 0.983 / 0.722 | 0.583 / 1.000 / 0.731 | 0.090 / 0.796 | 0.090 / 0.713 |
| seller | N/A / 0.000 / N/A | N/A / 0.000 / N/A | 1.000 / 0.500 | 1.000 / 0.500 |
| renter | N/A / 0.000 / N/A | N/A / 0.000 / N/A | 1.000 / 0.749 | 1.000 / 0.760 |
| media outreach | N/A / 0.000 / N/A | N/A / 0.000 / N/A | 1.000 / 0.294 | 1.000 / 0.452 |
| realtor network | N/A / 0.000 / N/A | N/A / 0.000 / N/A | 1.000 / 0.500 | 1.000 / 0.500 |
| other | 0.000 / 0.000 / 0.000 | 0.000 / 0.000 / 0.000 | 0.943 / 0.671 | 0.954 / 0.737 |

Buyer recall rises from 0.983 to 1.000 and buyer precision from 0.579 to 0.583. Buyer specificity stays 0.090: the same non-buyer messages are still called buyer. Buyer AUC falls from 0.796 to 0.713. The predicted class catches one more buyer, and the buyer probability ranks buyers less cleanly against the other messages.

Seller, renter, media outreach, and realtor network still have recall 0. Their specificity stays 1.000 because they are never the predicted class. Renter AUC moves from 0.749 to 0.760. Media-outreach AUC moves from 0.294 to 0.452. Those are ranking changes. The predicted label for those rows stays buyer or, for some media-outreach rows, other.

`other` precision and recall stay 0. Specificity rises from 0.943 to 0.954 because the model emits `other` once less. `other` AUC rises from 0.671 to 0.737.

### Per class, revised test labels

On this key, buyer precision is 0.662 for the Assignment 9 model and 0.667 for the retrained model. Buyer recall is 0.983 and 1.000. Buyer F1 is 0.789 and 0.798. Buyer specificity is 0.103 for both. Buyer AUC is 0.823 for the Assignment 9 model and 0.743 for the retrained model.

Renter recall stays 0. Its test support falls from 11 to 9 because V16 is in the test set twice and is now buyer. Media-outreach test support falls from 10 to 5 because V27 is in the test set five times and is now other. Seller and realtor network are unchanged.

## Confusion

Pooled counts. Rows are the reference label, columns are the prediction.

Assignment 9 baseline, original labels:

| Actual | buyer | seller | renter | media outreach | realtor network | other |
| --- | --- | --- | --- | --- | --- | --- |
| buyer | 55 | 0 | 0 | 0 | 0 | 1 |
| seller | 6 | 0 | 0 | 0 | 0 | 0 |
| renter | 11 | 0 | 0 | 0 | 0 | 0 |
| media outreach | 6 | 0 | 0 | 0 | 0 | 4 |
| realtor network | 2 | 0 | 0 | 0 | 0 | 0 |
| other | 15 | 0 | 0 | 0 | 0 | 0 |

Revised model, original labels: the same matrix, except buyer→buyer is 56 and buyer→other is 0.

That single changed prediction is V2 on repeat 9 (seed 50). V2 was not relabeled. Its `expand_other` label is buyer. The baseline called it other; the retrained model calls it buyer. On the original key, V16 (2 test appearances), V22 (6), and V27 (5) are predicted buyer by both models.

Baseline model, revised labels:

| Actual | buyer | seller | renter | media outreach | realtor network | other |
| --- | --- | --- | --- | --- | --- | --- |
| buyer | 63 | 0 | 0 | 0 | 0 | 1 |
| seller | 6 | 0 | 0 | 0 | 0 | 0 |
| renter | 9 | 0 | 0 | 0 | 0 | 0 |
| media outreach | 1 | 0 | 0 | 0 | 0 | 4 |
| realtor network | 2 | 0 | 0 | 0 | 0 | 0 |
| other | 14 | 0 | 0 | 0 | 0 | 0 |

Revised model, revised labels: the same matrix, except buyer→buyer is 64 and buyer→other is 0.

The reference change moves counts because those three messages were already predicted buyer:

- V16, test twice, renter→buyer: two renter→buyer cells become buyer→buyer.
- V22, test six times, other→buyer: six other→buyer cells become buyer→buyer.
- V27, test five times, media outreach→other: five media-outreach→buyer cells become other→buyer.

Those eight V16 and V22 test rows were wrong under `expand_other` and correct under the revised key, with no change in the predicted word. The five V27 rows stay wrong, because the model says buyer and the new label is other. The four media-outreach→other cells are V21, the Mount Dora email request, which both models still miss.

## Agreement and what the scores suggest

Krippendorff's alpha on the Assignment 7 file is 0.517 (five annotators, four categories, the original 30 messages). Alpha on the Module 10 form is 0.546 (four annotators, six categories, 30 form messages). The form shares 16 messages with Assignment 9. The raters and the category set also differ, so the 0.029 rise is a small gain on a new labeling round, not a before-and-after on one matrix.

On the 16 shared messages, 13 majorities match `expand_other` and 3 differ. Two of those three are 2–1–1 votes.

That agreement change does not show up as a classifier that separates the six classes. Minority-class recall stays 0 after retraining. The decision that changed is one buyer message, on one split, moving from other to buyer. The larger accuracy gain appears when V16 and V22 are scored as buyer, which is the label the baseline already predicted.

The pattern is that reported accuracy rises when the reference labels move onto the class the model already emits. It rises very little when the model is refit. Label agreement and label consistency can make a metric look better while the boundary still calls almost every message buyer. With one to four examples in the non-buyer classes, agreement among annotators does not create a training set that can identify those classes.

## Limit of this comparison

The intervention covered 16 of the 30 Assignment 9 messages and changed 3. The extra form messages include several realtor-network and media-outreach examples that this comparison never trains on. The results describe this 30-message set under the original splits. They do not estimate what the same classifier would do if it were trained on the full form set.

## Files

- `Module_10_assignment/retrain_classifier.py` runs the four evaluations.
- `Module_10_assignment/outputs/label_changes.csv` lists every match, retention, and exclusion.
- `Module_10_assignment/outputs/comparison_metrics.csv` has the side-by-side repeat means. Per-class means are in each experiment folder. The submission notebook is `revised_classifier.ipynb`.
- Each run has `class_metrics_summary.csv`, `repeat_summary.csv`, `confusion_matrix_sum.csv`, and `test_predictions.csv` under `outputs/baseline_on_original_labels/`, `outputs/revised_on_original_labels/`, `outputs/baseline_on_revised_labels/`, and `outputs/revised_on_revised_labels/`.
- `outputs/changed_item_predictions.csv` is the held-out predictions for V16, V22, and V27.
