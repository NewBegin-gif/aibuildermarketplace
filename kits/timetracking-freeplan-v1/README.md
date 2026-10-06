# Find where a free time-tracking plan stops before your team depends on it

Checklist version 1.0 (2026-10-06), AI Builder Marketplace. Full test report: https://officesoftwaremarketplace.com/jibble-review.html#hands-on

**Who this is for:** Small teams that want to run attendance and timesheets on Jibble's free plan and need to know, before payroll depends on it, which steps of their process the free plan covers.

**Scenario:** A team of a few people clocks in on the web, a manager checks the week, and the hours go to payroll as a file.

## Files

- `prompt.txt`: the build prompt, send it word for word
- `test-data.csv`: made-up test data (example.com addresses cannot receive mail)
- `expected-results.csv`: every check with its pass condition and room for your result
- `checklist.html`: the same checks as a printable page
- `decision-brief.html`: one printable page to record your must-haves, results, costs, open questions and decision
- `our-results.csv`: what we saw on 2026-09-25 (per builder where we compared several)

## Rules

- Use your own test organisation and addresses you own; no real staff data.
- Do not switch on face recognition or GPS for real people: a face profile is biometric data with legal duties attached.
- Note the trial day for every check. During the 14-day trial nothing is locked, so a check passed in week one can fail after day 14.
- Do not buy anything; the price table is behind the upgrade button.

Repair template: `Not applicable: write down what you saw, on which plan and on which day of the trial.`

## Checks

- **J01 Plan on day one**: The dashboard shows which plan you are on and whether a trial of paid features is running.
- **J02 Clock in and out**: Clock in and out a few times; note how it rounds and what it refuses.
- **J03 Second user**: Invite a second person; no payment prompt appears for the second user.
- **J04 Price behind the upgrade button**: The upgrade button shows the paid plans with prices per user, monthly and annual.
- **J05 What Free leaves out**: In the plan comparison, find each step your process needs (approvals, breaks, groups, attendance report, leave) and note whether Free has it.
- **J06 Export for payroll**: Export one week as a file and check the columns your payroll needs.
- **J07 After the trial**: After day 14, repeat J05 and J06: note what is now locked and whether the export still works on Free.
- **J08 Biometrics and location**: Find where face recognition and GPS are switched on and which plan has them; do not switch them on.

**Not covered:** One free account on the web on one day, during the trial; no real team over a real pay period, no mobile app or kiosk, and no payroll import tested.

A missing test is not a product failure. Our own results are one run per builder on the free plan; re-run the checks on the plan you would buy.

Licence: CC BY 4.0 (AI Builder Marketplace).
