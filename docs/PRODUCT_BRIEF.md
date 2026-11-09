# Product brief — NEXUS Freight

## Executive summary

NEXUS Freight is a proposed AI-native operating layer for global freight forwarders and logistics service providers. It connects the commercial and operational lifecycle of a shipment: request intake, rating, quote approval, booking, document processing, milestone visibility, exception resolution and freight finance.

The product is not positioned as another static dashboard or a full replacement for every Transportation Management System (TMS). Its initial wedge is to reduce repetitive coordination and document work while integrating with customers' existing TMS, ERP, carrier and partner systems.

## Target customer and buyer

**Initial ideal customer profile:** independent and mid-market freight forwarders / 3PLs handling recurring air and ocean shipments, with 10–250 operations users and fragmented email, spreadsheet and legacy TMS workflows.

- Economic buyer: owner, COO, Head of Operations, Managing Director.
- Champion: forwarding operations manager, pricing manager, customer service lead.
- Users: pricing analysts, documentation clerks, shipment operators, finance controllers.
- Secondary customer: shippers/distributors needing multi-forwarder visibility and vendor coordination.

## Jobs to be done

1. Turn incomplete requests into structured quote opportunities.
2. Calculate a reliable buy/sell rate and defend gross margin.
3. Convert accepted commercial offers into operational jobs without rekeying data.
4. Maintain a consistent shipment event history across providers.
5. Detect delays, customs holds, missing milestones and document gaps early.
6. Assign exception ownership and track resolution.
7. Reconcile customer receivables and carrier payables against shipment economics.
8. Measure lane, carrier, mode and customer profitability.

## Differentiation hypothesis

- AI-assisted workflow across the operational hand-offs, not just a chatbot.
- Canonical shipment/event model with standards-aware mappings.
- Human approval for consequential actions.
- Open integration strategy: add an intelligence layer around incumbent TMS/ERP systems.
- Commercial + operations + finance view connected to one shipment record.

These are hypotheses to validate with buyers. The prototype does not prove demand or a defensible moat by itself.

## MVP scope

Included in this prototype:
- Global command centre and synthetic route map.
- Shipment list, shipment creation, valid status transitions and timeline.
- Quote calculator, gross-margin pricing and quote conversion.
- Exceptions with severity, owner, next action and resolution state.
- Local text document extraction and field heuristics.
- Carrier, lane, mode, finance and customer analytics.
- SaaS pricing and unit economics scenario.
- Database-backed demo with SQLite / PostgreSQL connection support.

Not included / not represented as live:
- Live carrier pricing, schedules, bookings or tracking.
- Customs filing, eBL/eAWB issuance or regulated trade services.
- Real AI/LLM calls, OCR, ETA model or autonomous execution.
- Production identity management and multi-tenant security controls.
- Subscription billing, customer payment processing or bank reconciliation.
- Production mobile app, external customer portal or public API server.

## Product success metrics

### Commercial
- Qualified pilot-to-paid conversion.
- Annual recurring revenue (ARR) and net revenue retention.
- Gross margin after cloud, AI/OCR and support costs.
- Customer acquisition cost (CAC) payback.

### Operational
- Median quote turnaround time.
- Quote conversion rate.
- Manual touches per shipment.
- Document re-keying rate.
- Exception detection lead time.
- Time to resolve exceptions.
- Milestone completeness and freshness.
- Gross profit per shipment / lane.
- Days sales outstanding (DSO) and overdue receivables.

## Value hypothesis to validate

A pilot should baseline and measure a small number of outcomes, not make broad claims. Example pilot target hypotheses (not verified results):
- Reduce quote preparation time by 30–50% for a selected document/request type.
- Reduce manual data entry per shipment by 25–40%.
- Increase milestone completeness to more than 95% for connected providers.
- Reduce time from exception detection to owner assignment by 50%.
- Improve quote margin visibility before acceptance.

## Why now

The industry is moving toward more standardised data exchange and AI-assisted operations. McKinsey's May 2026 article describes AI-enabled logistics workflows already being used for quote handling, check calls, order acceptance and invoice workflows. DHL's 2026 Logistics Trend Radar identifies agentic AI as a high-impact force, while also stressing people, governance and responsible oversight. DCSA and IATA standards show a path toward more interoperable shipment-event and cargo data exchange.

## Business model hypothesis

- Subscription tiers by active shipments / users / connected integrations.
- Usage pricing for document processing and automation runs.
- Enterprise setup, integration and SLA fees.
- Later: partner/API ecosystem and transaction-linked products, subject to legal and regulatory design.

See `BUSINESS_MODEL.md` for illustrative packaging and scenario math.
