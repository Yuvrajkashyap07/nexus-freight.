# Deployment guide

## Streamlit Community Cloud (classroom demonstration)

1. Push the complete project folder to a GitHub repository.
2. Connect GitHub at https://share.streamlit.io/.
3. Select repository / branch and set the app file to `app.py`.
4. Use Python 3.12.
5. Deploy. Dependencies are pinned in `requirements.txt`.

### Secrets

For a shared deployment, add managed PostgreSQL credentials through Streamlit app secrets. Example:

```toml
NEXUS_DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require"
NEXUS_APP_MODE = "demo"
# Optional structured extraction; the operator must explicitly opt in per document
# OPENAI_API_KEY = "YOUR_API_KEY"
# OPENAI_MODEL = "gpt-6-luna"
```

Do not put a real database password in a repository. Use the Streamlit secrets UI or your hosting provider's secret manager.

## Local deployment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Docker

```bash
docker build -t nexus-freight .
docker run --rm -p 8501:8501 -v nexus-data:/app/data nexus-freight
```

For PostgreSQL, pass `NEXUS_DATABASE_URL` as a runtime secret/environment variable. Do not bake secrets into the image.

## Database options

- Local demo: SQLite database in `data/nexus_demo.db`.
- Shared demo / pilot: managed PostgreSQL. The app uses SQLAlchemy and will create the included tables on first launch.
- Commercial: managed PostgreSQL with migrations, backups, point-in-time recovery, tenant isolation, read replicas where needed and an operational restore test.

The included SQLAlchemy `create_all()` is suitable for this prototype; commercial releases should use Alembic migrations and a reviewed migration process.

## Deployment hardening

- Replace demo role picker with SSO/OIDC/SAML and user memberships.
- Set `NEXUS_APP_MODE=production` and disable all demo-reset functionality in a production build (the current app is a demo build; do not expose it to real operational users).
- Use external private object storage for raw documents. The demo stores extracted text in the database and does not persist uploaded binaries.
- For LLM extraction, use a data-processing agreement, regional processing review, customer opt-in, redaction policy and model output evaluation; do not send restricted documents without authorisation.
- Add tenant RLS / equivalent database isolation and API authorisation checks.
- Add background workers and managed queue for OCR, integrations, webhooks and notifications.
- Configure structured logs, monitoring, alerts, secrets rotation and backups.
- Run dependency, security and penetration testing.

## Troubleshooting

- **Module import failure:** use Python 3.12 and reinstall `requirements.txt`.
- **Database connection failure:** verify the full SQLAlchemy URL and `psycopg` driver; use `postgresql+psycopg://`.
- **Streamlit Cloud fails to build:** inspect deployment logs; check pinned package versions and Python selection.
- **No data:** app seeds the synthetic dataset on first run. Use Admin & Architecture → Reset synthetic demo dataset to restore it.
- **No file text extracted:** scanned PDF has no selectable text; OCR is not included in this demo.
