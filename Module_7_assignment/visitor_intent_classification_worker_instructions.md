# Worker instructions: Classify visitor first chat statements

## Task

You will read **one visitor message** at a time—the **first thing the visitor says** in a website chat transcript (after any agent greeting). Each message is labeled with an ID (for example, `A1`).

**Your job:** Assign **exactly one** intent label:

- `buyer`
- `seller`
- `renter`
- `other`

Use **only the text of that first visitor message**. Do not use later messages, email headers, or outside knowledge. Judge intent from what a reasonable reader would infer from the words the visitor used.

**Output format:** One line per message:

`A1, buyer`

Use lowercase labels only. No extra commentary unless your platform requires it.

---

## Category definitions

### `buyer`

The visitor shows interest in **acquiring** residential real estate—buying a home, condo, townhome, land, or investment property—or in **finding property to purchase** (including tours, listings, new construction, or pre-approval budgets).

Includes:

- Explicit buy/purchase language (“looking to buy,” “investment property,” “preapproval,” “make an offer”).
- House-hunting without the word “buy” (“looking for a home,” “see what’s available,” “look at houses,” “second home,” “relocate and need a single family home”).
- Buying for short-term rental, Airbnb, or vacation use (they still intend to **purchase**).
- Interest in a **specific listed property** they might buy (address given, “interested in this house”).

Does **not** include renting as a **tenant** (see `renter`) or selling their own property (see `seller`).

### `seller`

The visitor shows interest in **disposing of** property they own or will own—selling, listing, or getting help to sell.

Includes:

- “Sell my home,” “list my property,” “how soon can I sell,” “ready to sell.”
- Moving away and need to sell existing home (when **selling** is the stated goal of the message).

If the first message mentions **both** buying and selling, label the category that is **clearer or more prominent** in that message (more detail, stated first, or the main reason for the chat). If truly equal, choose `buyer` when they are trying to acquire Florida property and `seller` when the main ask is only to sell.

### `renter`

The visitor shows interest in **leasing** a home or apartment to **live in** as a tenant—not purchasing.

Includes:

- “Looking to rent,” “need a rental,” “lease a house/apartment,” bedroom/bath requirements for a **rental** they will occupy.
- “Rent first” / “rent before buying” when **renting** is the stated near-term goal of the message.

Does **not** include buying a property to rent out to others (that is `buyer`). Does **not** include asking only for **historical rental income** on a property they want to buy (that is `buyer`).

### `other`

The message does **not** clearly show intent to buy, sell, or rent property in the sense above.

Includes:

- Greetings only (“Hi,” “Hi there,” “Good morning”) with no housing intent.
- Name or identity only (“my name is …,” “sorry I was just chatting”).
- Verifying the agent or brand (“Are you with Ken Pozek’s team?”) with no buy/sell/rent ask.
- General information, media, or contact requests (“email for …,” “who are you?”).
- Area or environmental questions unrelated to a transaction (for example, whether a neighborhood is “a bad area” or how local conditions affect quality of life).
- Services that are not tenant rental or a purchase/sale (for example, **property management only** with no stated buy/sell/rent goal).
- Too vague or garbled to infer intent (“hI,” random fragments).

When unsure between `other` and a transaction category, ask: **Would a colleague clearly route this lead to sales (buy), listings (sell), or rentals (rent)?** If not, use `other`.

---

## Examples (one per category)

Examples below are illustrative; your assigned messages may differ.

| Label | Example first visitor message |
|-------|-------------------------------|
| **buyer** | `Hi xxxxx! My husband and I will be in town next week looking for a primary residency that we will turn into an Air BNB within the next year.` |
| **buyer** | `I need to speak to a agent who specializes in short term rentals and is attentive. We are looking to make offers on a short term rental today.` |
| **seller** | `I have two investment properties here that I would like to sell next summer.` |
| **renter** | `I am looking to rent a house 2/2 or 3/2., fenced yard and screened in porch. I work at xxxx at xxxxxxxxx Mall.` |
| **other** | `Hi there` |
| **other** | `Its said poinciana fl is a bad are is this true` |
| **other** | `Interested in a consultation` |

Additional **buyer** examples from the same study set (not in your A1–A30 batch):

- `Can you send me some information on the Lennar homes in Bridgewalk St Cloud?`
- `G'morning. Husband and I visiting Orlando area end of Jan to scope out a retirement home, but have no idea where to start looking.` (on a realtor site, scoping a retirement home = shopping to buy unless they say rent)

---

## Ambiguous or borderline messages

Follow these rules so labels stay consistent across workers.

1. **Greeting + intent.** If the message is mostly a greeting but includes a clear buy/sell/rent intent, use the transaction label, not `other`.  
   - `Hi xxxxx! … looking for a primary residency that we will turn into an Air BNB…` → `buyer`

2. **Investment / Airbnb / vacation rental purchase.** If they want to **buy** property to rent to guests or use part-time and rent the rest, label `buyer`, not `renter`.  
   - `…looking to make offers on a short term rental today` → `buyer`

3. **Rental rates on a purchase.** Asking about rental income or historical rates for a **specific home they might buy** is still `buyer`.  
   - `found a house we are interested in … would like to know historical rental rates for this property` → `buyer`

4. **Browsing listings.** “Just looking at your listings,” “look at potential property to buy,” or “see what’s available” → `buyer` when the context is shopping for property to own.

5. **Relocate / move.** “Relocate,” “moving to Orlando,” or “looking to move to [area]” without the word “rent” → usually `buyer` on a realtor site unless they explicitly want a lease.

6. **Rent vs buy later.** If they say they want to **rent first** or **rent now** as the main point → `renter`. If they only discuss buying with no rent plan → `buyer`.

7. **Sell + buy in one message.** Use the **dominant** intent in that first message (see `seller` definition). Do not use two labels.

8. **Property management.** A question only about whether the company offers management, with no stated plan to buy, sell, or rent a home → `other`.

9. **Unclear or minimal text.** Single letters, typos only, or messages where any of the three transaction intents would be a guess → `other`.

10. **Do not infer from stereotypes.** Base the label only on what is written in the first visitor statement.

---

## Quality checklist (before you submit)

- [ ] Exactly **one** label per message ID.
- [ ] Label is one of: `buyer`, `seller`, `renter`, `other` (lowercase).
- [ ] Decision based **only** on the first visitor statement.
- [ ] Borderline cases handled with the rules in **Ambiguous or borderline messages**.

---

## Reference file for this batch

Messages to classify: `Data/random_30_visitor_first_statements.txt` (IDs `A1`–`A30`).
