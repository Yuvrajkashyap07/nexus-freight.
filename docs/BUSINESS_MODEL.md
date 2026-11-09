# Business model, packaging and commercial assumptions

## Positioning

**NEXUS Freight is an AI-native operations layer for freight forwarders and logistics service providers.** It automates high-friction workflows across quote-to-cash while connecting to existing TMS/ERP and carrier ecosystems.

## Proposed initial customer

Independent and mid-market forwarders / 3PLs with recurring air and ocean freight, 10–250 operations users, several carrier partners and manual work across email, PDFs, spreadsheets and a legacy TMS.

## Monetisation model

1. Subscription tier based on active shipments, users and integration count.
2. Usage fees for OCR/LLM documents, enrichment and automated workflow runs.
3. Paid onboarding, migration, integration and training.
4. Enterprise tier for SSO, security controls, custom retention, SLA and dedicated support.
5. Later API/network services when the product has partner density and defensible operational data.

Avoid unlimited processing in early plans. Track cost per processed document, workflow, shipment, integration sync and customer support hour.

## Pricing hypothesis (not verified market rates)

| Plan | Monthly price hypothesis | Included volume | Intended customer |
|---|---:|---:|---|
| Launch | $149 | 250 active shipments/month, 3 users | Small forwarder trialling digital operations |
| Growth | $499 | 1,500 active shipments/month, 10 users | Growing independent forwarder |
| Scale | $1,499 | 7,500 active shipments/month, 30 users | Multi-team / multi-branch operator |
| Enterprise | Custom | Contracted | Large forwarder / 3PL / multinational |

The included volume above is a package-design assumption. Conduct buyer interviews and competitor procurement research before publishing a public price list.

## Value-based pricing

The price should be anchored to the cost of manual operations the product removes or accelerates. The pilot should quantify:

- Quote preparation minutes and staff cost per quote.
- Manual document-keying time per shipment.
- Customer status-check workload.
- Exception detection and resolution time.
- Billing and carrier-invoice reconciliation effort.
- Cost of missed milestones, storage/demurrage and margin leakage.

Do not use speculative “AI savings” as a price anchor. Measure actual baseline and post-pilot outcomes.

## Example ARR scenarios

| Customers | Average monthly subscription | ARR |
|---:|---:|---:|
| 500 | $400 | $2.4M |
| 2,500 | $650 | $19.5M |
| 10,000 | $1,000 | $120M |
| 20,000 | $1,000 | $240M |

Formula: customers × average monthly recurring revenue × 12. These are mathematical scenarios, not forecasts. They exclude implementation, usage fees, churn, discounting and bad debt.

## Unit economics model

Track at customer and plan level:

- MRR / ARR.
- Gross retention and net revenue retention.
- Gross margin after cloud, database, storage, OCR/LLM, messaging, carrier API and support costs.
- CAC by channel and segment.
- CAC payback period.
- Onboarding hours and integration costs.
- Usage distribution and cost-to-serve by shipment.
- Expansion revenue from additional users, branches and integrations.

A 75–85% mature software gross margin is a planning aspiration, not an assumption to hard-code. Early implementation-heavy accounts may be materially lower.

## Commercial controls

- Contracted rate cards and effective dates.
- Approval floors by customer, lane, mode and margin band.
- Separate buy and sell currency and record FX source/time.
- Quote expiry and surcharge validity.
- Customer credit-limit / overdue check before booking.
- Shipment-level accrual vs final carrier invoice reconciliation.
- Clear distinction between gross margin, markup, revenue, gross profit and cash collected.

## Go-to-market hypothesis

1. Start with one freight-forwarder segment and one workflow (e.g., email/PDF quote intake and quote preparation).
2. Recruit 3 design partners in one high-volume lane or mode.
3. Integrate with existing TMS/ERP rather than asking customers to rip and replace.
4. Sell a paid workflow pilot with a baseline, success criteria and operator training.
5. Expand from quoting to document validation, exception handling and finance only after proving adoption.
6. Add partner integrations and marketplace/network capabilities as distribution, not as day-one scope.

## Kill / pivot criteria

Pause or narrow the product if, after 20 qualified buyer interviews:
- fewer than 10 report the same costly workflow problem;
- fewer than 3 agree to design-partner access;
- fewer than 2 will pay for a narrow pilot;
- reliable data access requires integrations customers will not approve;
- measured time or error reduction is immaterial after a 6–8 week pilot.
