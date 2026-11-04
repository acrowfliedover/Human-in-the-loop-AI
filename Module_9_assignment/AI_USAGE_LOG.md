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
