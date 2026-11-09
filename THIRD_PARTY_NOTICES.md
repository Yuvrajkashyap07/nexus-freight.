# Third-party package notices

The project does not copy source code from third-party logistics repositories. It uses published Python packages via `requirements.txt`; each package retains its own licence.

| Package | Role | Upstream | Licence (verify on release) |
|---|---|---|---|
| Streamlit | Application UI/runtime | https://github.com/streamlit/streamlit | Apache-2.0 |
| pandas | Dataframes and analytics | https://github.com/pandas-dev/pandas | BSD-3-Clause |
| Plotly | Interactive charts | https://github.com/plotly/plotly.py | MIT |
| SQLAlchemy | Database ORM/engine | https://github.com/sqlalchemy/sqlalchemy | MIT |
| psycopg | PostgreSQL driver | https://github.com/psycopg/psycopg | LGPL-3.0-or-later / exceptions as published |
| pypdf | PDF text extraction | https://github.com/py-pdf/pypdf | BSD-3-Clause |
| python-docx | DOCX extraction | https://github.com/python-openxml/python-docx | MIT |
| openpyxl | XLSX extraction | https://foss.heptapod.net/openpyxl/openpyxl | MIT |

For a commercial release, generate a dependency SBOM, pin and scan dependencies, review the licence version actually installed, and preserve required notices. Do not treat this summary as legal advice.
