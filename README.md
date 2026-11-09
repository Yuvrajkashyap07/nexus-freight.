# NEXUS Freight — AI-native Global Logistics Operating System

**A professor-ready, deployable Streamlit prototype** for freight forwarders, 3PLs, distributors and cargo owners.

NEXUS Freight demonstrates one connected shipment workflow: customer request → quote → booking → documents → milestones → exception management → invoice control → network intelligence.

> **Demo disclaimer:** All preloaded companies, shipments, costs, invoices, carrier scores and events are synthetic. Real port/city names and coordinates are used only to make the sample lanes understandable. No live carrier, customs, AIS, GPS, airline or payment integrations are connected in this classroom build.

## 1. What is included

- Command centre with global lane map, shipment KPIs, operational risk radar and recent events.
- Shipment operations with filters, create-shipment form, legal status transitions and event timeline.
- Freight quote engine with cost stack, gross-margin pricing, quote pipeline and quote-to-booking conversion.
- SaaS packaging and unit-economics simulator.
- Exception queue with severity, assignment, status and audit log.
- Document desk supporting PDF, DOCX, XLSX, CSV and TXT extraction, logistics-field detection and document classification; optional OpenAI structured extraction is available when configured and explicitly enabled by the operator.
- Carrier and lane analytics, mode economics, finance ledger, receivables ageing and customer directory.
- Admin/architecture area with integration catalogue, entity map and go-live checklist.
- SQLite demo database; PostgreSQL connection support through `NEXUS_DATABASE_URL`.
- Seeded global sample network and repeatable synthetic demo reset.
- Unit tests, deployment files, architecture documentation and professor demo script.

## 2. Run locally

Recommended: Python 3.12.

```bash
# 1. Extract the ZIP and open the project folder
cd nexus-freight

# 2. Create an isolated environment
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\\Scripts\\activate    # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

Open `http://localhost:8501`.

The first run creates `data/nexus_demo.db` and inserts the synthetic dataset. The app is designed to work without paid API keys.

## 3. Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload the contents of this project folder.
2. Open [share.streamlit.io](https://share.streamlit.io/) and connect GitHub.
3. Choose the repository, branch and `app.py` as the main file.
4. Select Python 3.12 in Advanced settings (if shown).
5. Deploy. `requirements.txt` pins the application dependencies.
6. For a persistent database, provision managed PostgreSQL and add this secret in Streamlit app settings:

```toml
NEXUS_DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
NEXUS_APP_MODE = "demo"
# Optional: enable the AI extraction checkbox in Document Desk
# OPENAI_API_KEY = "YOUR_API_KEY"
# OPENAI_MODEL = "gpt-6-luna"
```

Never commit `.streamlit/secrets.toml`, API keys, database URLs or real customer documents. Streamlit's official documentation recommends entering secrets through app settings rather than committing them: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management

For an offline professor demo, local SQLite is sufficient. For a shared class deployment, configure managed PostgreSQL before asking multiple people to write to the same demo environment.

## 4. Demo personas

The sidebar has four **demo personas** so you can show role-aware screens:

- **Operations Manager:** shipment, exception and booking actions.
- **Pricing Analyst:** create and inspect freight quotes.
- **Finance Controller:** finance-focused read access.
- **Executive Viewer:** read-only dashboards.

This is a presentation convenience, **not real authentication or production RBAC**. Do not expose sensitive or customer data on a public Streamlit demo.

## 5. Core calculation

The quote engine uses gross margin rather than markup:

```text
Total buy cost = freight + fuel + origin handling + destination handling
                 + customs + insurance + other

Sell price = total buy cost / (1 - target gross margin)
Gross profit = sell price - total buy cost
Gross margin % = gross profit / sell price × 100
```

Example: $4,000 buy cost at 20% target gross margin gives $5,000 sell price and $1,000 gross profit. A 20% markup would produce a different result.

## 6. Document intelligence scope

The Document Desk defaults to local text extraction and deterministic field matching. It supports text-based PDF, DOCX, XLSX, CSV and TXT files up to 15 MB. Scanned PDFs need an OCR service/adapter, which is intentionally not bundled. An optional OpenAI Responses API adapter can perform structured field extraction when `OPENAI_API_KEY` is configured and the operator explicitly checks the opt-in control; only extracted text is sent, not the original file. The model output remains a suggestion for human review, not a customs or financial instruction.

## 7. What is demo-ready vs. not connected

| Capability | Current status |
|---|---|
| Global operations dashboard | Working with synthetic data |
| Shipment create/status workflow | Working; changes persist in configured DB |
| Quote calculation and quote-to-book conversion | Working |
| Exception creation and resolution | Working |
| Local document extraction | Working for supported text-based formats |
| Analytics / finance / SaaS plan scenario | Working against synthetic records |
| DCSA Track & Trace | Canonical mapping design; no carrier connection |
| IATA ONE Record | Canonical mapping design; no airline/forwarder connection |
| Carrier schedule/rate feeds | Not connected; credentials/commercial agreements required |
| Customs filing / eBL / eAWB | Not connected; partner access and compliance required |
| Real SSO / Google / Microsoft identity | Not connected; demo persona switch only |
| Billing / payment collection | Not connected; pricing model is illustrative |
| OCR | Not connected; scanned-document OCR requires a provider adapter |
| LLM extraction | Optional OpenAI Responses API adapter; requires customer-supplied key and explicit opt-in |
| Customer-facing portal / public API | Architecture target only |

## 8. Production evolution

Streamlit is used here because it is easy to deploy and strong for interactive data applications. It is a prototype/pilot shell, not the recommended long-term multi-tenant UI for a high-volume global logistics SaaS.

A production path is documented in `docs/SYSTEM_ARCHITECTURE.md`:

- Keep the domain model and service layer.
- Add a secure API gateway and dedicated worker services.
- Use managed PostgreSQL, object storage, queue/event bus and secrets manager.
- Add tenant isolation, enterprise SSO, permissions and audit retention.
- Connect carrier/TMS/customs partners through adapters and standard mappings.
- Add monitoring, backup/restore, incident response and penetration testing.

## 9. Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

## 10. Project map

```text
app.py                         Streamlit entry point
nexus/constants.py              Ports, modes, roles, status definitions
nexus/db.py                     SQLAlchemy data model + DB connection
nexus/seed.py                   Synthetic classroom data
nexus/services.py               Domain services and workflow rules
nexus/analytics.py              Read models and explainable risk signals
nexus/document_intelligence.py  Local document extraction and field detection
nexus/ui/                       Streamlit page modules
docs/                           Product, architecture, schema, economics, demo and research
sql/                            PostgreSQL hardening examples
sample_data/                    Safe sample documents and CSV extracts
tests/                          Unit tests
```

## 11. Research and standards

Start with `docs/RESEARCH_AND_COMPETITIVE_LANDSCAPE.md`. Important standards references include:

- DCSA Track & Trace: https://dcsa.org/standards/track-and-trace
- DCSA Industry Blueprint: https://reference.dcsa.org/content/standards/industry-blueprint/current/industry-blueprint
- IATA ONE Record: https://www.iata.org/one-record
- IATA ONE Record GitHub specification: https://github.com/IATA-Cargo/ONE-Record

## Licence

The application code in this repository is released under the MIT License. Third-party packages retain their own licences; see `THIRD_PARTY_NOTICES.md`.
