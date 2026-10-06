# Hand tickets over between two agents and check what the reports show

Checklist version 1.0 (2026-10-06), AI Builder Marketplace. Guide based on documentation: we have not run these checks ourselves.

**Who this is for:** Small support teams sharing one inbox who want to know, during a trial, whether handing tickets over, working on the same ticket and reporting per agent behave the way their team works.

**Scenario:** Two agents share a support inbox. One admin wants to see who handled what, and other departments only need to leave internal notes.

## Files

- `prompt.txt`: how to set up the trial
- `test-data.csv`: made-up test data
- `expected-results.csv`: every check with its pass condition and room for your result
- `checklist.html`: the same checks as a printable page

## Sources (read 2026-10-06)

- SupportBee docs: Assigning tickets to a User (updated 24 Jun 2026): https://supportbee.com/docs/handling-tickets/assigning-tickets-to-a-user
- SupportBee docs: Commenting on a ticket (updated 24 Jun 2026): https://supportbee.com/docs/handling-tickets/commenting-on-a-ticket
- SupportBee docs: Replying to Tickets (updated 28 Sep 2026): https://supportbee.com/docs/handling-tickets/replying-to-tickets
- SupportBee docs: Viewing the Audit Trail (updated 24 Mar 2026): https://supportbee.com/docs/handling-tickets/viewing-the-audit-trail
- SupportBee docs: Understanding User Permissions (updated 31 Mar 2026): https://supportbee.com/docs/users/understanding-user-permissions
- SupportBee docs: Tracking Performance with Reports (updated 24 Jun 2026): https://supportbee.com/docs/handling-tickets/tracking-performance-with-reports

## Rules

- Use a trial account and inboxes you own; never real customers or real customer data.
- Send the six test messages from a mailbox you control, so replies and notifications land somewhere you can check.
- Write down the plan, the roles you used, the date and the time window you look at in the reports.
- A report that shows less than you expect can come from roles, settings or assignment; check those before you call data missing.

Repair template: `Not applicable: write down what you saw and on which plan.`

## Checks

- **S01 Assign**: Assign three of the six tickets to Agent A and leave three unassigned. Per the docs, Agent A gets an email and finds them under My Tickets.
- **S02 Two agents on one ticket**: Open the same ticket as Agent A and Agent B. Per the docs, the second sees a red alert that someone else is viewing it, and a draft in progress shows a pencil in the list.
- **S03 Hand over with an internal note**: Agent A comments on a ticket and tags Agent B. Per the docs, B gets an email and the customer never sees comments; confirm nothing reached your sending mailbox.
- **S04 Reply and history**: Agent B replies. Per the docs, the ticket moves to Answered on its own and the audit trail shows who assigned, commented and replied, with times.
- **S05 Who sees reports**: Open Reports as admin, then as Agent A and as the collaborator. Per the docs, only admins can access reports.
- **S06 Reports against assignment**: Compare the overview with Agent A's report for your test window. Per the docs, agent and team reports count only assigned tickets (three, not six), and collaborator activity does not appear.
- **S07 Collaborator limits**: As the collaborator, try to comment, reply, assign and archive. Per the docs, commenting works and the other three do not; collaborators count as users on the price.

**Not covered:** This guide is based on SupportBee's documentation read on 6 October 2026; we have not run these checks ourselves. It does not cover email deliverability, the customer portal or integrations.

A missing test is not a product failure. Our own results are one run per builder on the free plan; re-run the checks on the plan you would buy.

Licence: CC BY 4.0 (AI Builder Marketplace).
