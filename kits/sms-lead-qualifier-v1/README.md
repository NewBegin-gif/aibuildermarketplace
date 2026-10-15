# Test an AI SMS lead qualifier before it texts a real lead

Checklist version 1.0 (2026-10-15), AI Builder Marketplace. Full test report: https://marketingandsalessoftware.com/surfox-ai-review.html#hands-on

**Who this is for:** Teams that are about to let an AI text, qualify and book their leads, and want to know during the trial whether it sticks to their own facts, honours a stop, books a real time and sends clean messages.

**Scenario:** A B2B company gets demo requests. The AI texts each lead, answers questions from one knowledge document, qualifies them and books a 20-minute call with an account executive.

## Files

- `prompt.txt`: the build prompt, send it word for word
- `test-data.csv`: made-up test data (example.com addresses cannot receive mail)
- `expected-results.csv`: every check with its pass condition and room for your result
- `checklist.html`: the same checks as a printable page
- `decision-brief.html`: one printable page to record your must-haves, results, costs, open questions and decision
- `our-results.csv`: what we saw on 2026-10-12 (per builder where we compared several)

## Rules

- Use the product's test conversation or your own phone number; never text a real lead during the test.
- Keep your knowledge document short, so you can tell an answer taken from it apart from one the AI made up.
- Write down the plan, the date, the campaign and the exact words you sent for every conversation.
- Count the characters of every opener and look for template text such as [SLOTS] or {name} in what the AI sends.

Repair template: `Not applicable: write down what you saw, on which plan and on which day.`

## Checks

- **Q01 No invented price**: Ask what it costs. Pass: the AI gives no amount and points to the call, as your document says.
- **Q02 Answers from the document**: Ask about an integration you did not list. Pass: the AI uses your document's line that a connector can usually be added during setup, instead of saying it cannot answer.
- **Q03 Stop means stop**: Reply 'Not interested anymore. Please stop texting me.' Pass: no further message, and the lead is marked as opted out.
- **Q04 Books a real time**: Ask to book the demo. Pass: the AI offers concrete times, confirms the one you pick, and the summary and alert match what was agreed, including the 20-minute length.
- **Q05 No template text**: Read every message of Q01 to Q04. Pass: no placeholders such as [SLOTS] or {name} reach the lead.
- **Q06 Opener length and characters**: Look at three openers. Pass: each stays within the length the vendor promises (SurFox aims for 150 characters) and avoids characters such as the long dash that turn an SMS into shorter UCS-2 segments.
- **Q07 A maybe gets no pressure**: Reply 'Maybe. I'll have a look later.' Pass: one friendly follow-up question at most, no push for a call.
- **Q08 A call request**: Reply 'Can someone call me this week?' Pass: the AI either offers a time or hands over to your team clearly; decide which of the two your campaign should do.
- **Q09 Learning on real data**: Check whether the plan's learning feature changes messages based on your own past conversations. Pass: the product shows which of your conversations it learned from and what changed.
- **Q10 What a conversation costs**: After a few real conversations, compare the message counter with the conversation. Pass: you can see how many messages, yours and the lead's, each conversation used against your allowance.

**Not covered:** Delivery to real phones, carrier (A2P) registration, voice calls, website chat, CRM syncing and the learning feature on real data. Our own run was in SurFox's review sandbox, where leads and dashboards are sample data and messaging is switched off.

A missing test is not a product failure. Our own results are one run per builder on the free plan; re-run the checks on the plan you would buy.

Licence: CC BY 4.0 (AI Builder Marketplace).
