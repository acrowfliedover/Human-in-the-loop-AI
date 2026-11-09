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

## 2026-11-08 — Thirty form messages and clearer six-label instructions

- **Prompt:** Select 30 first visitor messages from the Module 7 chats, covering all six categories with at least two strong examples each, plus some borderline messages the instructions can still decide. Save the messages in Module 10, and revise the instructions for a Google Form where each message is a multiple-choice question.
- **AI response summary:** Read the first visitor line from the ReadyChat emails and saved 30 of them in `Module_10_assignment/form_messages.txt`. Buyer is the largest group (11). Seller, renter, media outreach, and realtor network each have at least two clear messages, and several items are borderline on purpose. Replaced the instructions with a fixed six-step order in `visitor_intent_form_instructions.txt` for the form description, and mirrored that text in `visitor_intent_worker_instructions.md`. Redacted one street address, one email, and one phone number.
- **Accepted / changed / rejected:** Pending user review. The form file does not show the answer labels.
- **Issues found:** The email pool has no reporter or interview request. Media outreach is defined as asking for a named person’s email or a call with that person, which matches messages that are actually in the chats. Seller is any request to sell a home they own, including two messages that also describe a later purchase.

## 2026-11-08 — Censor names and separate examples from questions

- **Prompt:** Censor names, personal information, and company names in the instructions and the 30 questions, using (name). Keep every form message out of the instruction examples.
- **AI response summary:** Replaced people, companies, teams, video platforms, emails, phone numbers, and the street address in `form_messages.txt` with (name). Rewrote the six examples in `visitor_intent_form_instructions.txt` and `visitor_intent_worker_instructions.md` so none of them repeat a question. City and neighborhood names used to describe the home search were left in place.
- **Accepted / changed / rejected:** Pending user review.
- **Issues found:** None. A check confirmed no example sentence is contained in a form message, and no form message is contained in the instructions.

## 2026-11-08 — Restore public names and locations

- **Prompt:** Put public companies such as YouTube and Airbnb back. Censor only names that identify the data provider. Leave cities, states, and similar locations visible.
- **AI response summary:** Restored Airbnb, YouTube, Disney's Golden Oaks, Serenity Townhomes, Keller Williams, and visitor names that are not the chat team. `(name)` remains only for the team’s agents and the team name. The instruction line now says `(name)` is a person on the real estate team. Examples were left unchanged, so they still do not repeat a question.
- **Accepted / changed / rejected:** Pending user review. The visitor email, phone number, and street address in questions 14 and 15 are visible again because they do not name the data provider.
- **Issues found:** None.

## 2026-11-08 — Match instructions to edited placeholders

- **Prompt:** The names in the questions were edited by hand. Update the instructions to match.
- **AI response summary:** The questions now use (name), (company head figure), (company name), (address), [email], and [phone]. Both instruction files explain each placeholder and say none of them changes the category. The category rules and examples were left as they were.
- **Accepted / changed / rejected:** Pending user review.
- **Issues found:** None.

## 2026-11-08 — Krippendorff's alpha on the five-annotator labels

- **Prompt:** Use Krippendorff's alpha on `Module_7_assignment/labeled_visitor_intent.csv`, write the work, result, and analysis as a text file in Module 10, and justify alpha over Cohen's kappa and Fleiss's kappa.
- **AI response summary:** Computed nominal alpha on the five annotator columns (30 items, no missing cells). Alpha is 6857/13264 = 0.517, with a 10,000-item bootstrap interval of 0.346 to 0.660. Wrote `Module_10_assignment/krippendorff_alpha_analysis.txt` with the coincidence matrix, disagreement mass by item, Fleiss's kappa (0.514), the ten pairwise Cohen kappas (0.330 to 0.701), and the boundary analysis. `final_label` was left out of the rater matrix.
- **Accepted / changed / rejected:** Pending user review. No labels were changed.
- **Issues found:** None on the point estimate; the coincidence matrix was checked against the item counts. Numpy was not installed, so the bootstrap was not cross-checked against a second library.
