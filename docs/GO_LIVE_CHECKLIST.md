# Production go-live checklist

This is deliberately stricter than a classroom presentation checklist. A logistics platform can affect cargo, customer commitments, customs documents and payments; a polished UI is not production readiness.

## Product and customer validation
- [ ] Interview 20–30 qualified freight forwarders / 3PLs across at least two markets.
- [ ] Choose one beachhead workflow (e.g., quote intake, document checking or shipment exception handling).
- [ ] Secure at least three design partners with authorised data access.
- [ ] Agree pilot baseline, success metrics, user owner and commercial sponsor.
- [ ] Prove ROI with before/after workflow data; do not rely on generic AI productivity claims.

## Legal, commercial and data
- [ ] Define data controller/processor roles and execute DPAs.
- [ ] Review cross-border transfers and data residency for each launch market.
- [ ] Define data retention, deletion, legal hold and backup retention.
- [ ] Review liability boundaries for ETA, customs, cargo release and payment instructions.
- [ ] Confirm licensing rights for standards, carrier data, rate data, maps and partner APIs.
- [ ] Define customer terms, SLA, support hours, incident communication and service credits.
- [ ] Establish acceptable use and cargo/document handling policies.

## Identity and security
- [ ] Implement SSO/OIDC or SAML, MFA and account lifecycle management.
- [ ] Add organisation membership and role/permission assignments.
- [ ] Enforce tenant isolation at the API and database layers; test cross-tenant access.
- [ ] Add least-privilege service accounts and short-lived credentials.
- [ ] Store secrets in a cloud secret manager; rotate credentials.
- [ ] Encrypt data in transit and at rest; manage keys and access logs.
- [ ] Add upload malware scanning, MIME sniffing, file-size limits and secure object references.
- [ ] Add rate limiting, input validation, CSRF protection where applicable and abuse monitoring.
- [ ] Complete threat modelling, SAST, dependency scanning and independent penetration test.

## Reliability and operations
- [ ] Move long-running work to background workers with retries and dead-letter queues.
- [ ] Add idempotency for all partner events, quote creation and invoice ingestion.
- [ ] Add outbox pattern to publish events only after successful DB transactions.
- [ ] Define uptime, latency, queue-age and event-freshness SLOs.
- [ ] Add structured logs, distributed traces, metrics and actionable alerts.
- [ ] Configure database backups, point-in-time recovery and restore drills.
- [ ] Define incident response, on-call, escalation and customer status-page process.
- [ ] Load test realistic shipment, milestone and document volumes.

## Logistics integrations
- [ ] Select carrier / visibility partners and complete commercial onboarding.
- [ ] Implement DCSA Track & Trace mapping and conformance tests where applicable.
- [ ] Implement IATA ONE Record mapping and secured API onboarding for air cargo where applicable.
- [ ] Validate UN/LOCODE, IATA codes, timezones, equipment and commodity reference data.
- [ ] Map customer TMS/ERP master data and define source-of-truth per field.
- [ ] Test event ordering, duplicates, missing events, reversals, transshipment and partial delivery.
- [ ] Add partner outage handling and manual fallback workflows.

## AI and decision governance
- [ ] Establish an evaluation dataset for each document type, carrier event and recommendation.
- [ ] Measure field-level precision/recall and false-positive/false-negative rates.
- [ ] Use confidence thresholds and human review for low-confidence or high-impact decisions.
- [ ] Version prompts, models, extraction schemas and business rules.
- [ ] Record provenance of AI-generated recommendations and human approvals.
- [ ] Prevent autonomous customs filings, cargo release and payments without approved controls.
- [ ] Monitor model drift, prompt injection and data leakage.

## Finance and pricing
- [ ] Validate rate sources, surcharge rules and effective dates.
- [ ] Implement multi-currency accounting and timestamped FX rates.
- [ ] Reconcile quoted vs actual carrier costs and customer invoices.
- [ ] Define approval matrix for below-floor margin and customer credit exposure.
- [ ] Validate local tax, invoicing and accounting requirements for each market.
- [ ] Add payment processor only after underwriting and finance controls.

## Launch acceptance criteria
- [ ] Two paid pilots show measurable improvement in a selected workflow.
- [ ] No unresolved critical security findings.
- [ ] Tenant-isolation tests pass.
- [ ] Backup restore test passes.
- [ ] Partner conformance and failure-mode tests pass.
- [ ] AI/document evaluations meet agreed thresholds.
- [ ] Customer support, training and rollback runbooks are ready.
