# Operational workflows and business rules

## 1. Request-to-quote

**Inputs:** customer, origin, destination, mode, equipment, cargo, gross weight, volume, incoterm, service level, ready date, delivery deadline and requested terms.

**Process:** normalise request → validate mandatory fields → retrieve relevant rate cards → calculate accessorials/surcharges → apply customer contract → calculate gross margin → apply approval threshold → create versioned quote → send through approved channel.

**Controls:** rate effective date, currency, minimum margin, customer credit status, quote validity, surcharge expiry and approval history.

## 2. Quote formula

```text
buy_total = base_freight + fuel + origin_handling + destination_handling
            + customs + insurance + other
sell_price = buy_total / (1 - gross_margin_pct)
gross_profit = sell_price - buy_total
markup_pct = gross_profit / buy_total
```

Example:

- Buy total: $4,000
- Target gross margin: 20%
- Sell price: $5,000
- Gross profit: $1,000
- Markup on cost: 25%

The app deliberately distinguishes gross margin from markup.

## 3. Quote acceptance to booking

Accepted quote snapshot is converted to a shipment/job record. Keep quoted buy/sell economics immutable as the commercial baseline; operational actual costs may arrive later. Booking confirmation creates a milestone and an audit event.

Production extension: customer acceptance evidence, booking request/confirmation API, partner reference, equipment allocation and booking amendment workflow.

## 4. Milestone processing

Inbound sources may include carrier API/webhook, terminal message, EDI, TMS, customer portal or manual authorised update.

1. Authenticate and validate source.
2. Persist raw payload / hash.
3. Resolve provider references to shipment/equipment.
4. Map source event to canonical event.
5. Check idempotency key.
6. Validate state and event chronology.
7. Append milestone, update shipment projection, publish internal event.
8. Recalculate ETA/risk and evaluate exception rules.
9. Notify assigned owner / customer based on preferences.

## 5. Exception management

Categories: ETA at risk, customs/documentation, capacity/rollover, damage/shortage, milestone gap, invoice mismatch and other.

Severity should consider operational impact, customer priority, cargo sensitivity, time to deadline and financial exposure. The prototype uses explainable starter rules rather than an opaque ML model.

Every exception requires a description, owner, recommended next action, status and resolution evidence. Critical or financial exceptions require escalation rules and an SLA clock in production.

## 6. Status transitions in the demo

Draft → Quoted / Cancelled

Quoted → Booked / Cancelled

Booked → In transit / Exception / Cancelled

In transit → Customs hold / Exception / Delivered

Customs hold → In transit / Exception / Delivered

Exception → In transit / Customs hold / Delivered

Delivered / Cancelled are terminal in the prototype.

A production state machine must support mode-specific journeys, transshipments, partial deliveries, split/merge shipments, equipment return and amendment/reversal events.

## 7. Document processing

Supported demo formats: text-based PDF, DOCX, XLSX, CSV, TXT.

Pipeline: file validation → file-type/size check → extraction → document classification → field heuristics → field-coverage estimate/warnings → human review → attach to shipment.

Production pipeline: private object upload → malware scan → OCR/layout extraction → model-assisted field extraction with schema validation → confidence thresholds → reviewer queue → approved fields written to shipment/document records → audit log.

Never auto-file customs, release cargo, issue regulated documents or commit financial values solely on low-confidence extraction.

## 8. Finance and settlement

Maintain separate receivable and payable records, currency, due dates, status, references and reconciliation evidence. Apply FX rates and tax rules explicitly; do not combine currencies by simply summing amounts. The current demo ledger is a teaching model, not a general ledger or tax-compliant accounting system.
