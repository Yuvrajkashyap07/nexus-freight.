# Professor demo script (7–10 minutes)

## Opening (45 seconds)

“NEXUS Freight is an AI-native operating layer for freight forwarders. The problem we are addressing is operational fragmentation: quotation requests, documents, shipment milestones, exceptions and finance often live across emails, PDFs, spreadsheets and separate systems. Our product connects those workflows around one shipment record. This is a working classroom prototype using synthetic data.”

## 1. Command Centre (1 minute)

- Show active shipments, on-time delivery, open exceptions, receivables and gross-profit pipeline.
- Point to the global lane map; explain that the locations are real but transactions are synthetic.
- Explain the operational risk radar: transparent baseline rules based on customs hold, ETA and missing milestone signals; not a trained ML ETA predictor.

## 2. Shipment Operations (1.5 minutes)

- Search for a shipment reference.
- Open the shipment record and show customer, carrier, mode, lane, equipment, ETA and financial snapshot.
- Show the event timeline.
- Update a shipment through an allowed status transition and show the new milestone / audit event.
- If time allows, create a new shipment using the form.

## 3. Quote & Pricing (1.5 minutes)

- Build a quote using base freight, fuel, handling, customs, insurance and other cost components.
- Explain that the system uses gross margin correctly: sell price = buy cost / (1 − margin).
- Save a quote and show the quote pipeline.
- Convert a draft/sent quote into a booked shipment and explain that the shipment inherits the commercial quote snapshot.

## 4. Document Desk (1 minute)

- Upload one sample document from `sample_data/`.
- Show document classification and extracted fields.
- Explain that extraction defaults to local deterministic parsing. If an API key is configured, the operator can explicitly opt in to structured AI extraction; the extracted text (not the source file) is sent to the model. Show schema validation and human review; scanned PDFs still need OCR.

## 5. Exceptions and Insights (1.5 minutes)

- Open an ETA risk or customs exception.
- Reassign the owner and move the exception to In progress or Resolved.
- Show carrier scorecard, mode economics, lane profitability and AR/AP ledger.

## 6. Commercial model and architecture (1.5 minutes)

- Open Quotes & Pricing → Platform Pricing and Unit Economics.
- Explain that tiers are price hypotheses and must be validated in buyer interviews.
- Open Admin & Architecture and show system diagram, integration catalogue and data model.
- Call out DCSA Track & Trace and IATA ONE Record as standards-aware integration targets, not live connections.

## Closing (30 seconds)

“Our first wedge is a narrow operations workflow, not an attempt to replace every TMS. We would validate with 20 forwarder interviews, three design partners and at least two paid pilots. We would measure quote turnaround, manual touches per shipment, milestone completeness and exception-resolution time before expanding.”

## Suggested professor questions and answers

**Is the AI connected to real carriers?** No. The prototype uses synthetic event data and deterministic rules. Carrier connectivity requires contracts, credentials, mapping and conformance testing.

**Why Streamlit?** It makes a functional data-heavy prototype easy to share for assessment. The long-term SaaS front end and API would be separated from workers and the database.

**How is this different from CargoWise?** The thesis is an integration-friendly AI operations layer around existing systems, not a full TMS rip-and-replace. That differentiation still needs buyer validation.

**How does the company make money?** Subscription tiers based on shipment volume, users and integrations, plus usage fees and enterprise integration/SLA packages.

**What is the hardest part?** Data access and trust: carrier/TMS integrations, document quality, exception accuracy, liability boundaries and workflow adoption.
