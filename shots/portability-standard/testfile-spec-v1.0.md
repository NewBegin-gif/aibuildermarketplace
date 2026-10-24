# Software Portability Test, v1.0

Publisher: AIBuilder Marketplace Research. Released specification: 24 October 2026.
Licence for this specification and our synthetic kits: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Attribute AIBuilder Marketplace Research and identify changes. Vendor quotations and screenshots retain their respective rights.

## Purpose and scope

Record what survives one documented export and update/re-import of a small synthetic dataset on a named product, plan and test date. The result is a table of checks, not a score, ranking, certification or market-wide claim. It does not establish complete account portability, regulatory compliance, contract rights or support for untested plans.

Use one released category kit and record its ID, exact version and file hashes. Keep a copy of its kit.json. The release manifest accompanying this specification pins 17 category kits. Each fixture contains exactly AIBM-001 and AIBM-002; vendor-native identifiers are separate. Only controlled fictitious data may be used. Do not invite external people, connect a real mailbox or pay for an upgrade to finish this protocol.

## Categories

The immutable kit files are part of this specification. Each category has its own `kit.json`, two-record `fixture.csv`, README, and two synthetic attachments. All 17 kits initially use version 1.0.0. Their input field mappings and category-specific refusal rules remain normative, including where the Dutch fixture documentation is more detailed than this summary.

| Kit ID | Category and test object | Boundary |
|---|---|---|
| crm-contacten | CRM: contact | Contact fields; no deal history |
| email-nieuwsbrief | Email/newsletters: subscriber | Subscriber fields; no campaign history or deliverability |
| facturatie-boekhouding-bonnen | Invoicing/accounting/receipts: financial record | Selected record and document; no complete ledger migration |
| documenten-esigning | Documents/e-signing: unsigned document | Unsigned PDFs and metadata; no signature request or audit-trail restoration |
| projecten-taken-feedback | Projects/tasks/feedback: task or feedback item | Selected items; no complete workspace graph |
| hr-roosters | HR/rosters: employee or roster item | Synthetic records; no payroll correctness |
| formulieren-quizzen | Forms/quizzes: response | Responses and fields; no form-logic equivalence |
| bestandsopslag | File storage: file | Downloaded bytes and metadata; no full permission tree |
| support-kennis-ai | Support/knowledge/AI: ticket or knowledge item | Selected object; no complete conversation or AI migration |
| chat-telefonie | Chat/telephony: contact/internal note | No calls, SMS, live chat, delivery or recording restoration |
| content-media | Content/media: content item | Record and asset; inspect documented media transformations |
| boekingen-evenementen | Bookings/events: booking | Synthetic booking data; no real invitations or payments |
| voorraad-producten | Inventory/products: product | Selected products; no stock reconciliation |
| leren-gebruikers | Learning/users: learner | Synthetic users; no course/progress completeness claim |
| monitoring-vermeldingen | Monitoring/mentions: local mention | Offline synthetic comparison; without a seed route, the affected check remains not_tested |
| databases-tabellen | Databases/tables: row | Selected rows and fields; no complete application migration |
| financiele-consolidatie | Financial consolidation: synthetic company | Two balanced synthetic companies; derived account rows must be documented; no financial statement assurance |

Use the category's actual entity and refusal rules from `kit.json`; these summaries do not grant additional exceptions. If a field is refused during input, record that limitation rather than later calling it export loss.

## Procedure

1. Record product, canonical review URL, plan, date, account limitations and kit ID/version/hashes. Establish a clean, isolated test scope.
2. Import the two fixture records. Record refused fields and distinguish an import loss from an export loss. Where supported, add the supplied attachment to each record and record native IDs.
3. Export through the route available to that plan. Record route, formats offered, actual delivery and whether the delivered bytes were opened. An offered format or emailed link is not a file inspection.
4. Compare the inspected export with the two source records. Keep demo/system rows separate. Apply all ten kit checks below and record evidence for every outcome.
5. Copy the actual export, retain its native IDs, and change only the field and value specified by kit.json.reimport for AIBM-002. Re-import as an update into the isolated scope. Never replace native IDs with AIBM IDs.
6. Export again. Check exactly two test records, unchanged AIBM-001, stable native IDs, only the specified AIBM-002 change, and preserved attachments/metadata. Record system updated_at separately. If re-import is unavailable, do not infer that it succeeded or failed.
7. Publish only English observations and redacted evidence. Never publish the native-ID export or re-import file. Publish only the original approved synthetic input with its SHA-256.

## Required result table

Use the exact ten check IDs and how-to instructions from the selected kit: records_returned, free_text_returned, custom_field_returned, date_returned, decimal_amount_returned, two_tags_returned, unicode_returned, attachment_returned, native_id_returned, reimport_update_only.

Each row contains the check ID, separate export and re-import outcomes, a short English observation with evidence, test date and the canonical review evidence URL. Keep per-record outcomes for AIBM-001 and AIBM-002, scope, field/native-ID mappings, evidence references, run ID and observed_on in the private meetlog kit block, following meetlog-kit-template.json. Pin kit.id, kit.version and kit.kit_json_sha256. The reimport_update_only export phase remains not_tested (not applicable). The allowed outcomes are:

- kept: the applicable value or relationship was checked and retained under the kit's comparison rules;
- lost: a value present at the relevant stage was demonstrably missing from the inspected result; identify the stage;
- changed: the inspected value, relationship or record count differs beyond permitted normalisation;
- not_offered: the plan or entity does not offer the relevant field/action; record the observed limitation;
- not_tested: the check was not completed, unavailable evidence was not inspected, or the result remains uncertain; give the reason.

The fixed checks mean:

| Check ID | Observation required in each applicable phase |
|---|---|
| records_returned | Both external IDs exactly once; count test records separately from system rows |
| free_text_returned | Multiline text, commas, quotes and line breaks retained |
| custom_field_returned | Separate custom field, mapped to the correct record |
| date_returned | Same calendar date; document equivalent notation |
| decimal_amount_returned | Exact decimal value and currency; compare with decimal arithmetic |
| two_tags_returned | Exact two-tag set; delimiter and ordering may differ |
| unicode_returned | Unicode characters preserved after NFC normalisation |
| attachment_returned | Download bytes, check record association, filename and SHA-256; document kit-permitted transformations |
| native_id_returned | Native identifier retained as a string and distinguished from external test_id |
| reimport_update_only | Same two records and native IDs; only AIBM-002 free_text updated; no duplicate; AIBM-001 and existing metadata/assets unchanged except documented system audit fields |

No native ID, editable text field or update import means reimport_update_only=not_offered with evidence. A business-key experiment may be additional evidence but cannot satisfy this fixed native-ID scenario. Preserve the raw export and every conversion recipe. A mapping error remains not_tested until corrected. Record cancellation friction separately; it is not an eleventh scored check.

Normalise only what kit.json explicitly allows, including line endings, Unicode NFC, documented equivalent dates and decimal notation. A URL to an attachment is not retained attachment bytes. Empty or missing evidence is not kept. There is no aggregate passed/failed verdict. A successful row does not establish that other records, integrations, permissions or entire accounts transfer.

## Provenance, vendor submissions and badge

A vendor submission is vendor-reported until our team repeats the same kit version in our own recorded session. A vendor submission alone never authorises a badge. Retain it for manual moderation via the existing vendor-answer workflow; no automatic publication or new portal is required. Reply with your run: kit ID/version/hashes, plan/date, ten-row result table and non-sensitive evidence. Do not send credentials or customer data.

A badge means only exit-tested by AIBuilder Marketplace on the stated date with the stated kit version. It links to #exit-test on the canonical review, including a sister-site canonical. It must never say passed. It expires twelve calendar months after the test, or immediately when a new kit version changes checks. At least one export check must have inspected evidence (kept, lost or changed); a run consisting solely of unknown or unsupported checks cannot authorise a badge. Even a current badge may include lost, changed or not_tested rows; readers must inspect the table.

## Versioning

Pin both the specification version and the independent category-kit version/hash. Never replace the bytes of a released kit. Incompatible changes to fields, checks, expected outcomes or re-import semantics require a new major kit version; compatible metadata additions may be minor and wording corrections without measurement changes may be patch releases. Any changed check set invalidates badges for the prior check set, even if incorrectly released under an unchanged version. Publish a new specification version when the procedure or outcome meanings change. Historical runs retain their original versions and are not silently rescored.

## Meaning of “passed”

This standard does not issue a product-level “passed” result. A retained value is evidence for that row, stage, scope and date only. Neither an exit-tested badge nor ten kept observations proves complete migration, absence of lock-in, future compatibility, security, regulatory compliance, cancellation rights or overall product quality. Never convert unknown or unsupported rows into successes.

## Licence notice

Copyright 2026 AIBuilder Marketplace Research. This specification and the supplied synthetic fixtures are licensed under Creative Commons Attribution 4.0 International (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/ . You may share and adapt them with attribution, a licence link and an indication of changes, without implying endorsement. Third-party product material is excluded. This licence does not grant use of the verification badge without meeting the badge policy.
