# Research and competitive landscape

**Research cut-off:** 9 November 2026. This is a focused product research memo, not an exhaustive review of every global logistics technology vendor.

## 1. Market and technology signals

### AI is moving from assistance to operational execution

McKinsey's 8 May 2026 article, *Code and cargo: How AI could change freight logistics*, describes AI-enabled systems being used for pricing, capacity sourcing, tracking and documents. It reports examples from logistics companies automating check calls, order acceptance, paper invoice payments and large-scale quote work. McKinsey also cautions that AI could reduce the moat of conventional logistics software interfaces, which supports the thesis for an operational intelligence layer but raises the bar for defensibility.

Source: https://www.mckinsey.com/industries/logistics/our-insights/code-and-cargo-how-ai-could-change-freight-logistics

### DHL sees agentic AI as a high-impact logistics trend

DHL's Logistics Trend Radar 8.0, announced 24 September 2026, identifies agentic AI and AI analytics as major forces. DHL describes AI moving from answering questions to planning, coordinating and taking actions alongside people. The report also highlights AI ethics, cybersecurity, workforce changes, supply-chain diversification and decarbonisation.

Sources:
- https://group.dhl.com/en/media-relations/press-releases/2026/ai-takes-action-while-people-remain-at-the-center-of-logistics-finds-dhl-logistics-trend-radar.html
- https://www.dhl.com/ae-en/home/innovation-in-logistics/logistics-trend-radar.html

### Interoperability is an industry requirement, not a slogan

DCSA Track & Trace defines common event semantics for shipment, transport, equipment, IoT and reefer events. DCSA's 2026.Q1 industry blueprint describes shipment journeys from booking and documentation through release and invoice settlement. The project should use a canonical event model and standards adapters rather than build provider-specific one-off logic into the core application.

Sources:
- https://dcsa.org/standards/track-and-trace
- https://reference.dcsa.org/content/standards/industry-blueprint/current/industry-blueprint
- https://reference.dcsa.org/content/standards/industry-blueprint/current/industry-blueprint-shipment-journey

### Air cargo data is moving to ONE Record

IATA describes ONE Record as a standard for data sharing through a common shipment record and secured web API. The July 2026 endorsed release includes Ontology 3.3.0 and API 2.3.0; IATA noted that ONE Record became the preferred data-sharing standard in air cargo from 1 January 2026.

Sources:
- https://www.iata.org/one-record
- https://iata-cargo.github.io/ONE-Record/2026-07/General/release-note/

## 2. Competitive categories

| Category | Examples | Strength | NEXUS entry hypothesis |
|---|---|---|---|
| Global forwarding / TMS | CargoWise, Descartes, Magaya, Riege, GoFreight, Logitude | Deep forwarding workflows, customs, accounting and ecosystem links | Do not replace core TMS initially; automate cross-system exception and document work |
| Digital freight forwarders | Flexport and regional digital forwarders | Digital customer experience, rates and freight execution | Sell software to asset-light forwarders, not compete as a carrier/forwarder |
| Visibility platforms | project44, FourKites, Shippeo, GoComet | Tracking, predictive visibility, network integrations | Add operational action and case ownership after visibility signal |
| Rate / booking tools | Freightos, WebCargo and carrier portals | Rate discovery, comparison and booking | Integrate where access is licensed; focus on internal quote workflow and margin controls |
| Procurement / supply chain suites | SAP, Oracle, Manhattan, Blue Yonder | Enterprise breadth, ERP/WMS/TMS depth | Start with a narrower user experience and partner with incumbent systems |

Vendor references (product scope evolves; validate features and terms directly):
- CargoWise / WiseTech Global: https://www.wisetechglobal.com/
- Descartes: https://www.descartes.com/
- Magaya: https://www.magaya.com/
- Riege: https://www.riege.com/
- GoFreight: https://www.gofreight.com/
- Logitude World: https://www.logitudeworld.com/
- Flexport: https://www.flexport.com/
- project44: https://www.project44.com/
- FourKites: https://www.fourkites.com/
- Shippeo: https://www.shippeo.com/
- Freightos: https://www.freightos.com/
- GoComet: https://www.gocomet.com/

## 3. Competitive gap to test

A likely opening is not “a new TMS with AI.” Incumbents have extensive process depth and partner networks. The product hypothesis is an **AI operations layer** that:

1. ingests unstructured requests and operational updates across email/PDF/EDI/API;
2. writes validated, reviewable data into existing systems;
3. watches milestones and commercial commitments;
4. identifies exceptions and suggests the next action;
5. routes tasks to the right operator with an auditable approval trail;
6. measures the resulting time saved and margin leakage avoided.

The product's moat would need to come from integrations, workflow adoption, historical exception resolution data, rate/contract context, partner network density and trust—not merely from its user interface or choice of LLM.

## 4. Initial customer discovery questions

- Which TMS/ERP is the system of record? Which data can be read and written?
- How many quote requests arrive per day and via which channels?
- What percentage require manual rekeying or clarification?
- Which lanes / modes generate the largest repeat volume?
- What are the top 5 exception categories by frequency and financial impact?
- How are ETAs sourced, corrected and communicated?
- How are carrier invoices reconciled with quotes and final shipment cost?
- What software is already purchased but underused?
- Who owns the budget and what procurement/security reviews are required?
- Would the customer pay for a narrow add-on, and what measurable outcome must it achieve?

## 5. Research caveats

- Industry case studies and vendor case studies may be selected for positive outcomes; do not treat them as independent benchmarks.
- Forwarder software pricing is often quote-based. The plan prices in this app are hypotheses, not competitor price quotations.
- Shipment volume, number of forwarders and global freight spend are not the same as software addressable market.
- The demo uses synthetic records and deterministic risk rules. It does not establish AI model accuracy, real carrier coverage or customer ROI.
