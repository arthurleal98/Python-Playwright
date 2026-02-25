import json
import base64
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import requests

# --- Constantes para o Bootstrap (para um relatório autônomo) ---
BOOTSTRAP_CSS_URL = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
BOOTSTRAP_JS_URL = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"

def get_embedded_assets():
    """Busca o CSS e JS do Bootstrap para embutir no relatório."""
    try:
        css = requests.get(BOOTSTRAP_CSS_URL).text
        js = requests.get(BOOTSTRAP_JS_URL).text
        return css, js
    except requests.exceptions.RequestException as e:
        print(f"Aviso: Não foi possível buscar os assets da CDN: {e}. O relatório não será estilizado.")
        return "", ""

def image_to_base64(image_path: Path) -> str | None:
    """Converte um arquivo de imagem para um data URI Base64."""
    if not image_path.is_file():
        print(f"Aviso: Imagem não encontrada em {image_path}")
        return None
    
    # Assume PNG baseado no contexto, mas poderia ser mais genérico
    mime_type = "image/png"
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded_string}"

def process_test_data(data: dict, base_dir: Path) -> dict:
    """Processa os dados do teste, embutindo imagens como Base64."""
    for test_id, test_results in data.get("tests", {}).items():
        for result in test_results:
            for extra in result.get("extras", []):
                if extra.get("format_type") == "image":
                    # O caminho no JSON é "screenshots\\arquivo.png". Pathlib lida com isso.
                    relative_path = Path(extra["content"])
                    full_path = base_dir / relative_path
                    base64_uri = image_to_base64(full_path)
                    if base64_uri:
                        extra["content"] = base64_uri
    return data

def generate_modern_html(data: dict, embedded_css: str, embedded_js: str) -> str:
    """Gera um novo relatório HTML moderno a partir dos dados processados."""
    
    # --- Funções auxiliares para o template ---
    def get_status_badge(status):
        status_map = {
            "Passed": "success",
            "Failed": "danger",
            "Skipped": "secondary",
            "Error": "danger",
            "XFailed": "warning",
            "XPassed": "info",
        }
        badge_class = status_map.get(status, "primary")
        return f'<span class="badge bg-{badge_class}">{status}</span>'

    def format_log(log_text):
        # Escapa caracteres HTML para evitar problemas de renderização
        escaped_log = (
            log_text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        # Destaca as linhas de erro (começando com 'E ' ou '> ')
        highlighted_log = re.sub(
            r"^(E .*|&gt; .*)$",
            r'<span class="text-danger fw-bold">\1</span>',
            escaped_log,
            flags=re.MULTILINE,
        )
        return f'<pre class="bg-light p-3 rounded small"><code>{highlighted_log}</code></pre>'

    # --- Calcula o Resumo ---
    all_tests = [result for results_list in data["tests"].values() for result in results_list]
    total_tests = len(all_tests)
    passed_count = sum(1 for t in all_tests if t["result"] == "Passed")
    failed_count = sum(1 for t in all_tests if t["result"] in ["Failed", "Error"])
    
    # --- Constrói as partes do HTML ---
    
    # Tabela de Ambiente
    env_html = ""
    for key, value in data.get("environment", {}).items():
        val_str = ""
        if isinstance(value, dict):
            val_str = "<ul>" + "".join(f"<li><strong>{k}:</strong> {v}</li>" for k, v in value.items()) + "</ul>"
        else:
            val_str = str(value)
        env_html += f"<tr><th class='w-25'>{key}</th><td>{val_str}</td></tr>"

    # Accordion de Resultados dos Testes
    tests_html = ""
    for i, (test_id, test_results) in enumerate(data["tests"].items()):
        result = test_results[0] # Assume um resultado por teste
        status = result["result"]
        
        # Conteúdo do corpo do Accordion
        body_content = ""
        if result.get("log"):
            body_content += f'<h6>Traceback & Log</h6>{format_log(result["log"])}'
        
        for extra in result.get("extras", []):
            if extra["format_type"] == "image":
                body_content += f'''
                    <h6 class="mt-3">Screenshot da Falha</h6>
                    <a href="{extra["content"]}" target="_blank" title="Clique para abrir em nova aba">
                        <img src="{extra["content"]}" class="img-fluid rounded border" alt="Screenshot para {test_id}">
                    </a>
                '''

        tests_html += f"""
        <div class="accordion-item" data-status="{status}">
            <h2 class="accordion-header" id="heading-{i}">
                <button class="accordion-button {'collapsed' if status == 'Passed' else ''}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{i}" aria-expanded="{'true' if status != 'Passed' else 'false'}" aria-controls="collapse-{i}">
                    <div class="d-flex justify-content-between w-100 align-items-center pe-3">
                        <span class="font-monospace text-truncate" style="max-width: 65%;">{test_id}</span>
                        <span class="ms-auto me-3">{get_status_badge(status)}</span>
                        <span class="text-muted small">{result['duration']}</span>
                    </div>
                </button>
            </h2>
            <div id="collapse-{i}" class="accordion-collapse collapse {'show' if status != 'Passed' else ''}" aria-labelledby="heading-{i}">
                <div class="accordion-body">
                    {body_content if body_content else "<p>Sem detalhes adicionais.</p>"}
                </div>
            </div>
        </div>
        """

    # --- Monta o HTML Final ---
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br" data-bs-theme="light">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Relatório de Testes Moderno</title>
        <style>
            {embedded_css}
            body {{ padding-top: 2rem; padding-bottom: 2rem; background-color: #f8f9fa; }}
            .accordion-button:not(.collapsed) {{ background-color: #e9ecef; }}
            .accordion-button:focus {{ box-shadow: none; }}
            .font-monospace {{ font-size: 0.9em; }}
            /* Estilos para os cards de filtro */
            .filter-card {{
                cursor: pointer;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }}
            .filter-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            }}
            .filter-card.active {{
                border: 3px solid #0d6efd; /* Cor primária do Bootstrap */
            }}
        </style>
    </head>
    <body>
        <main class="container">
            <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
                <h1 class="display-6">Relatório de Execução de Testes</h1>
                <p class="text-muted mb-0">Origem: {data.get('title', 'report.html')}</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-4 mb-3">
                    <div id="filter-all" data-filter="all" class="card text-center h-100 filter-card">
                        <div class="card-body">
                            <h5 class="card-title">Total de Testes</h5>
                            <p class="card-text fs-1 fw-bold">{total_tests}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div id="filter-passed" data-filter="Passed" class="card text-white bg-success text-center h-100 filter-card">
                        <div class="card-body">
                            <h5 class="card-title">Passaram</h5>
                            <p class="card-text fs-1 fw-bold">{passed_count}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4 mb-3">
                    <div id="filter-failed" data-filter="Failed" class="card text-white bg-danger text-center h-100 filter-card">
                        <div class="card-body">
                            <h5 class="card-title">Falharam</h5>
                            <p class="card-text fs-1 fw-bold">{failed_count}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="accordion mb-4" id="environmentAccordion">
                <div class="accordion-item">
                    <h2 class="accordion-header" id="env-heading">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#env-collapse" aria-expanded="false" aria-controls="env-collapse">
                            Ambiente de Execução
                        </button>
                    </h2>
                    <div id="env-collapse" class="accordion-collapse collapse" aria-labelledby="env-heading">
                        <div class="accordion-body">
                            <table class="table table-bordered table-sm">
                                {env_html}
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <h2>Resultados dos Testes</h2>
            <div class="accordion" id="testResultsAccordion">
                {tests_html}
            </div>
            <div id="no-tests-message" class="alert alert-info mt-3" style="display: none;">
                Nenhum teste corresponde ao filtro selecionado.
            </div>
        </main>
        <script>
            {embedded_js}
        </script>
        <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const filterCards = document.querySelectorAll('.filter-card');
            const testItems = document.querySelectorAll('#testResultsAccordion .accordion-item');
            const noTestsMessage = document.getElementById('no-tests-message');

            function updateActiveCard(activeCard) {{
                filterCards.forEach(card => card.classList.remove('active'));
                if (activeCard) {{
                    activeCard.classList.add('active');
                }}
            }}

            filterCards.forEach(card => {{
                card.addEventListener('click', () => {{
                    const filter = card.getAttribute('data-filter');
                    let visibleCount = 0;

                    updateActiveCard(card);

                    testItems.forEach(item => {{
                        const status = item.getAttribute('data-status');
                        // Considera 'Failed' e 'Error' como falhas
                        const isFailedOrError = status === 'Failed' || status === 'Error';

                        let shouldShow = false;
                        if (filter === 'all') {{
                            shouldShow = true;
                        }} else if (filter === 'Passed' && status === 'Passed') {{
                            shouldShow = true;
                        }} else if (filter === 'Failed' && isFailedOrError) {{
                            shouldShow = true;
                        }}

                        if (shouldShow) {{
                            item.style.display = 'block';
                            visibleCount++;
                        }} else {{
                            item.style.display = 'none';
                        }}
                    }});

                    noTestsMessage.style.display = visibleCount === 0 ? 'block' : 'none';
                }});
            }});

            // Inicia com o filtro "Total" ativo por padrão
            document.getElementById('filter-all').classList.add('active');
        }});
        </script>
    </body>
    </html>
    """

from pathlib import Path
from datetime import datetime
import json
from bs4 import BeautifulSoup

def main():
    """Função principal para executar a transformação."""

    # Define a raiz do projeto como base_dir
    base_dir = Path(__file__).resolve().parent  

    input_file = base_dir / "relatorio.html"

    # Cria um diretório de saída único para esta execução
    reports_base_dir = base_dir / "reports"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = reports_base_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "relatorio_moderno.html"

    if not input_file.is_file():
        print(f"Erro: Arquivo de entrada não encontrado em {input_file}")
        return

    print("Lendo relatório original...")
    with open(input_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    data_container = soup.find("div", id="data-container")
    if not data_container or not data_container.get("data-jsonblob"):
        print("Erro: Não foi possível encontrar o bloco de dados JSON no relatório HTML.")
        return

    print("Extraindo e processando dados dos testes (embutindo imagens)...")
    test_data = json.loads(data_container["data-jsonblob"])
    processed_data = process_test_data(test_data, base_dir)

    print("Buscando assets para um relatório autônomo...")
    css, js = get_embedded_assets()

    print("Gerando relatório HTML moderno...")
    modern_html = generate_modern_html(processed_data, css, js)

    print(f"Salvando novo relatório em {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(modern_html)

    print(f"\nTransformação completa! Abra o arquivo em: {output_file.resolve()}")


if __name__ == "__main__":
    main()