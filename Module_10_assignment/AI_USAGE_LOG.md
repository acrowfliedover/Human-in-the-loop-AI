# AI Usage Log

How AI was used on the Module 10 assignment. Newest entries are at the bottom.

## 2026-11-06 — Six-category worker instructions

- **Prompt:** Using the Assignment 7 visitor messages, write clearer and shorter labeling instructions for six categories (buyer, seller, renter, media outreach, realtor network, other) and store them with the assignment.
- **AI response summary:** Added `visitor_intent_worker_instructions.md`. Workers read only the first visitor message, assign one lowercase label, and stop at the first matching category in a fixed order. Examples are illustrative and are not copied from the 30 labeled messages. Media outreach is limited to coverage or a press contact. Realtor network is limited to other professionals or a team or brokerage check. Area questions and unlabeled contact requests stay in other.
- **Accepted / changed / rejected:** Pending user review. Did not relabel the Assignment 7 or Assignment 9 CSVs, and did not change the classifier. The file was first written under `Module_9_assignment/` and then moved here.
- **Issues found:** These rules would not copy the current `expand_other` overrides. The email request (V21) and the algae question (V27) would be `other`, not `media outreach`, because the message does not say the writer is press.

## 2026-11-06 — Move instructions to Module 10

- **Prompt:** Move any changes to the Module 10 assignment folder.
- **AI response summary:** Moved `visitor_intent_worker_instructions.md` from `Module_9_assignment/` to `Module_10_assignment/`. Removed that task's entry from the Module 9 usage log and recorded it here. Added Module 10 to `.cursor/rules/ai-usage-log.mdc`.
- **Accepted / changed / rejected:** Pending user review. Assignment 9 classifier files were left in place.
- **Issues found:** None.
