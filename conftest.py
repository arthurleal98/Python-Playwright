import os
import pytest
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv

# ====================================================
# 🔧 Configuração inicial
# ====================================================

load_dotenv()
FAIL_FAST_FLAG = "_fail_fast_triggered"

# ====================================================
# 🔐 Login credentials (generic names for public repo)
# ====================================================

@pytest.fixture(scope="session")
def credentials():
    # environment variable names have been changed to generic placeholders
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")
    missing = [name for name, value in {"TEST_USERNAME": username, "TEST_PASSWORD": password}.items() if not value]
    if missing:
        raise RuntimeError(f"Define the environment variables: {', '.join(missing)}")
    return {"username": username, "password": password}

# ====================================================
# 🚨 Fail-Fast Controlado (após última tentativa)
# ====================================================

@pytest.fixture(autouse=True)
def fail_fast_guard(request):
    """Interrompe a execução de testes seguintes se uma falha final ocorrer."""
    session = request.node.session
    if getattr(session, FAIL_FAST_FLAG, False):
        pytest.skip("Testes seguintes bloqueados devido a falha anterior definitiva.")

# ====================================================
# 📸 Screenshot e Retry Handling
# ====================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook que:
      - Gera screenshots em falhas.
      - Ignora 'fail-fast' enquanto o pytest-rerunfailures ainda está reexecutando.
      - Só marca 'fail-fast' na falha final (não recuperável).
    """
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    # Apenas na fase principal de execução
    if report.when == "call":
        # Detecta se esta execução está marcada como rerun
        is_rerun = getattr(report, "outcome", "") == "rerun"

        # Captura screenshot se falhou e a fixture "page" estiver presente
        if call.excinfo and "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            screen_file = str(screenshot_dir / f"{slugify(item.nodeid)}.png")

            try:
                page.screenshot(path=screen_file)
                print(f"Screenshot salvo: {screen_file}")
                if pytest_html:
                    extra.append(pytest_html.extras.png(screen_file))
            except Exception as e:
                print(f"[WARN] Falha ao capturar screenshot: {e}")

        # Só aplica fail-fast quando for falha final (não rerun)
        if report.failed and not getattr(report, "wasxfail", False) and not is_rerun:
            setattr(item.session, FAIL_FAST_FLAG, True)
            print("Falha definitiva detectada. Ativando fail-fast.")

    report.extra = extra
