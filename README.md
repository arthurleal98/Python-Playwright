# Automated End-to-End Test Suite (Playwright + Pytest)

## Overview
This repository hosts an example end-to-end testing framework written in Python using Pytest and Playwright. It illustrates a Page Object design, optional SQL Server database lookups for supporting data, and automatic HTML reporting with screenshots on failure.

> **Note:** the original draft contained names of internal portals and sample credentials; those have been stripped or replaced with placeholders suitable for public sharing. No proprietary code or real passwords are present.

## Requirements
- Python 3.11+ (pip included)
- Playwright browsers (python -m playwright install)
- ODBC Driver 17 for SQL Server if you intend to access databases via pyodbc
- (Linux) optional build dependencies for Playwright: python -m playwright install-deps

## Quick start
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate    # Windows
   source .venv/bin/activate     # Linux/macOS
   ```
2. Install Python requirements:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   python -m playwright install
   ```
4. Copy `.env.example` to `.env` and fill in real values for your target system. **Never commit real credentials.**

## Environment variables (.env)
The project uses python-dotenv to load settings in conftest.py and page classes. PORTAL1_BASE_URL and PORTAL2_BASE_URL are just sample names; you may rename them, but ensure they match the ones read by the login pages.

Example .env contents:

```env
# credentials used for both portals
TEST_USERNAME=your_user
TEST_PASSWORD=your_pass

# base URLs of the two applications under test
PORTAL1_BASE_URL=https://portal1.example.com/
PORTAL2_BASE_URL=https://portal2.example.com/

# optional database connections (generic names)
DB1_DRIVER=ODBC Driver 17 for SQL Server
DB1_SERVER=
DB1_DATABASE=
DB1_USERNAME=
DB1_PASSWORD=
DB1_TRUST_SERVER_CERT=true
DB1_TRUSTED_CONNECTION=false

DB2_DRIVER=ODBC Driver 17 for SQL Server
DB2_SERVER=
DB2_DATABASE=
DB2_USERNAME=
DB2_PASSWORD=
DB2_TRUST_SERVER_CERT=true
DB2_TRUSTED_CONNECTION=false
````

> Keep .env out of version control (it's ignored by .gitignore).

## Project layout
- `tests/`: Pytest test cases (see `test_proposta.py` for an example workflow).
- pages/: Page Objects encapsulating UI interactions.
- utils/: utility helpers such as DatabaseClient for querying SQL Server.
- dados.json: simple JSON file used to persist data between test runs.
- screenshots/: automatically populated with images on test failure.
- `execution_reports/`: HTML reports produced by `run_and_report.py`.    

## How the test flow works
1. Login to the first portal and create a booking (data loaded from dados.json).
2. Save proposal/booking numbers to dados.json for reuse.
3. Login to the second portal and perform a cargo integration using the previously created booking.

Page classes hide selectors and common actions, simplifying maintenance. The DB helper may be called by tests for generating or validating data.

## Running tests
### Using pytest directly
- Run full suite:
  `ash
  pytest --headed
  `
- Execute just the booking flow:
  `ash
  pytest tests/test_proposta.py --headed -k criar_booking
  `

### Automated script with reporting
The helper 
un_and_report.py wraps pytest and generates a custom HTML report:

`ash
python run_and_report.py                  # all tests
python run_and_report.py tests/test_proposta.py::test_integracao_carga_com_sucesso
`

Artifacts are placed under execution_reports/<timestamp>/ and include JUnit XML, raw Playwright data, and 
elatorio_custom.html.

### Simple report
executar_teste.py is a lightweight shortcut that invokes pytest with pytest-html and post-processes the result via modificador_relatorio.py.

## Evidence & data management
- Screenshots captured automatically on failure (see pytest_runtest_makereport in conftest.py).
- dados.json holds shared information; delete or reset it to start fresh.
- llure-results/ may be used to generate Allure reports (llure serve allure-results).

## Useful commands
- Update Playwright: pip install -U playwright && python -m playwright install
- Install Linux deps (CI): python -m playwright install-deps
- Run tests in parallel: pytest -n auto

## Troubleshooting
- Login errors: verify base URLs and credentials in .env.
- SQL connection failures: check ODBC driver, firewall, and DB parameters.
- Missing browsers: rerun python -m playwright install.
- Fail-fast trigger blocking further tests: clear __pycache__ and rerun after fixing root cause.

## Contributing
1. Create a new branch from main.
2. Add or modify tests using the Page Object pattern.
3. Run pytest locally and ensure reports are clean.
4. Submit a pull request with a description and any test data requirements.

---

For questions about architecture or adding new flows, review the classes under pages/ and leverage existing components to keep tests consistent.
## License
This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.
