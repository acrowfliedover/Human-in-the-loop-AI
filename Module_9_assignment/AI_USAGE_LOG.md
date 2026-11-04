# AI Usage Log

How AI was used on the Module 9 assignment. Newest entries are at the bottom.

## 2026-11-02 — Module 9 AI usage log

- **Prompt:** In the Module 9 assignment folder, put any new AI usage logs for this new assignment from now on.
- **AI response summary:** Added `Module_9_assignment/AI_USAGE_LOG.md` and updated `.cursor/rules/ai-usage-log.mdc` so Module 9 work is logged there. Module 3 and Module 4 logs were left unchanged.
- **Accepted / changed / rejected:** Pending user review. Assumed folder name `Module_9_assignment` and markdown log `AI_USAGE_LOG.md`, matching Modules 3 and 4.
- **Issues found:** The Module 9 assignment folder did not exist yet, so it was created for the log.

## 2026-11-02 — Baseline classifier recommendation

- **Prompt:** What algorithm or training method should be used for the Module 7 labeled visitor-intent data in Assignment 9?
- **AI response summary:** Recommended TF-IDF unigrams plus L2 logistic regression, evaluated with leave-one-out out-of-fold probabilities. Counted the 30 final labels (buyer 19, other 7, renter 3, seller 1) and noted media outreach and realtor network are absent unless an existing "other" message is relabeled.
- **Accepted / changed / rejected:** Pending user review. No code or labels were changed.
- **Issues found:** None. Course lecture notes were not in the repo, so the recommendation follows the assignment constraints and the 30-row class counts.

## 2026-11-03 — Six-class baseline notebook

- **Prompt:** Use `Module_9_assignment/labeled_visitor_intent.csv` and the `expand_other` six-class labels. Build a notebook with the TF-IDF logistic regression settings, training on 20 random messages and testing on the other 10, with a setting to repeat that run 10 times.
- **AI response summary:** Added `Module_9_assignment/baseline_classifier.ipynb`. It keeps `final_label`, trains on normalized `expand_other`, and runs 10 unstratified 20/10 splits (seeds 42 through 51). Each split refits TF-IDF unigrams and balanced logistic regression on the training rows only. The notebook writes per-class precision, recall, F1, specificity, and one-vs-rest AUC, macro averages, predictions, and the pooled confusion matrix under `Module_9_assignment/outputs/`.
- **Accepted / changed / rejected:** Pending user review. The earlier leave-one-out recommendation was replaced by the requested 20/10 repeated random splits.
- **Issues found:** Macro F1 looks stronger than the model is, because classes the model never predicts are N/A and drop out of the average. The notebook states that and reports mean accuracy 0.550, with 0 of 44 pooled non-buyer test rows correct.
