# Build a class-booking app and try to break it

Checklist version 1.0 (2026-09-26), AI Builder Marketplace. Full test report: https://aibuildermarketplace.com/research/one-booking-app-three-ai-builders/

**Who this is for:** Anyone deciding between AI app builders for a small booking, sign-up or reservation app: whether the builder handles capacity, double bookings, a protected admin page, export and data that survives republishing.

**Scenario:** A one-person yoga studio takes class bookings. Visitors book, move or cancel; only the owner sees and cancels all bookings and exports them.

## Files

- `prompt.txt`: the build prompt, send it word for word
- `test-data.csv`: made-up names and example.com addresses (they cannot receive mail)
- `expected-results.csv`: every check with its pass condition and room for your result
- `checklist.html`: the same checks as a printable page
- `our-results.csv`: what we saw on 26 September 2026, per builder (first version and after repairs)
- `simultaneous-bookings.js`: the ten-requests-at-once test for check T05

## Rules

- Send the prompt word for word as the first message, in a new project, and keep the same mode for every message.
- Change no code yourself: you are testing the builder, not your own programming.
- Allow at most three repair rounds, each with the repair template.
- Use only made-up test data (the test-data.csv file uses example.com addresses, which cannot receive mail).
- Write down the plan, the mode, the date and the credit balance before and after each message.

Repair template: `These tests fail: <list with test number, what you did, what you saw>. Fix only these, change nothing else, and republish.`

## Checks

- **T01 App published**: Loads at a public URL without logging in to the builder.
- **T02 Schedule**: Next 14 days; Mon-Fri 07:00 and 18:30, Sat 09:00, no Sunday; 8 spots each.
- **T03 Booking**: Name and email; spots left drops by one, also after a reload.
- **T04 Confirmation**: Confirmation shows a unique manage link.
- **T05 Full is full**: Ten simultaneous booking requests on an empty 8-spot class: 8 accepted, 2 refused. One manual double click is not this test; use simultaneous-bookings.js.
- **T06 No double booking**: The same email cannot book the same class twice, also typed in capitals.
- **T07 Move**: The manage link moves a booking: old class +1, new class -1.
- **T08 Cancel**: The manage link cancels a booking and frees the spot.
- **T09 Manage link not guessable**: The link contains a long random code, not a sequence number.
- **T10 Admin page protected**: No access without or with a wrong password, in the page and through the app's own API.
- **T11 Password not exposed**: The admin password is not in the page source, the JavaScript or any URL.
- **T12 Overview**: The admin page lists all bookings per class, consistent with T03-T08.
- **T13 Admin cancels**: The admin cancels a booking; the spot is freed and the status visible.
- **T14 CSV export**: Download with exactly: class date, class time, name, email, status; rows match what you booked.
- **T15 Input checks**: An empty name, a name of only spaces and an invalid email are refused by the server.
- **T16 Data survives**: Bookings are still there after a reload and after republishing.
- **T17 Usable on a phone**: At 390 px wide, schedule, booking and manage link work without sideways scrolling.
- **T18 Take it with you**: Export the code (GitHub or zip) and the data; try to run it outside the builder and note what does not come along.

**Not covered:** Not a security audit beyond T09 and T11, no load test beyond ten requests, no payments, email or real traffic, and one run per builder.

A missing test is not a product failure. Our own results are one run per builder on the free plan; re-run the checks on the plan you would buy.

Licence: CC BY 4.0 (AI Builder Marketplace).
