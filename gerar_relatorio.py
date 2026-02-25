# gerar_relatorio.py (versão modificada para usar caminho da imagem)

import base64
import mimetypes
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from slugify import slugify


def get_screenshot_path(test_name, class_name, execution_path, screenshot_sources):
    """Localiza o caminho absoluto do screenshot associado a um teste."""
    try:
        if not screenshot_sources:
            return None

        if isinstance(screenshot_sources, (str, bytes, os.PathLike)):
            screenshot_sources = [screenshot_sources]

        normalized_sources = []
        for source in screenshot_sources:
            if not source:
                continue
            abs_source = os.path.abspath(source)
            if os.path.exists(abs_source) and abs_source not in normalized_sources:
                normalized_sources.append(abs_source)

        if not normalized_sources:
            return None

        file_slug = ""
        if class_name:
            test_file = class_name.replace(".", os.path.sep) + ".py"
            file_slug = slugify(test_file)

        full_test_slug = slugify(test_name) if test_name else ""
        test_name_base = test_name.split("[")[0] if test_name else ""
        browser = ""
        if test_name and "[" in test_name and test_name.endswith("]"):
            browser = test_name.split("[")[1][:-1].lower()

        directory_prefixes = []
        if file_slug and test_name_base:
            base_prefix = f"{file_slug}-{slugify(test_name_base)}"
            if browser:
                directory_prefixes.append(f"{base_prefix}-{browser}")
            directory_prefixes.append(base_prefix)

        file_candidates = []
        if file_slug and full_test_slug:
            file_candidates.append(f"{file_slug}-{full_test_slug}")
        elif full_test_slug:
            file_candidates.append(full_test_slug)

        for base_dir in normalized_sources:
            try:
                base_entries = os.listdir(base_dir)
            except OSError:
                continue

            for prefix in directory_prefixes:
                for entry in base_entries:
                    entry_path = os.path.join(base_dir, entry)
                    if os.path.isdir(entry_path) and entry.startswith(prefix):
                        try:
                            png_files = sorted(
                                file_name
                                for file_name in os.listdir(entry_path)
                                if file_name.lower().endswith('.png')
                            )
                        except OSError:
                            continue
                        if png_files:
                            return os.path.join(entry_path, png_files[0])

            for slug in file_candidates:
                png_path = os.path.join(base_dir, f"{slug}.png")
                if os.path.isfile(png_path):
                    return png_path

        return None
    except Exception as exc:
        print(f"Erro ao processar screenshot para {test_name}: {exc}")
        return None


def build_data_uri(image_path):
    """Converte a imagem para um data URI Base64."""
    try:
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'image/png'
        with open(image_path, 'rb') as image_file:
            encoded = base64.b64encode(image_file.read()).decode('ascii')
        return f"data:{mime_type};base64,{encoded}"
    except OSError as exc:
        print(f"Aviso: não foi possível ler {image_path}: {exc}")
        return None


def parse_test_results(xml_input_file, screenshot_sources, execution_path=None):
    """Lê o arquivo XML e extrai os dados de cada teste, agrupando por arquivo."""
    tree = ET.parse(xml_input_file)
    root = tree.getroot()
    execution_base = os.path.abspath(execution_path or os.path.dirname(xml_input_file))
    test_results_by_file = {}
    summary = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'duration': float(root.find('testsuite').get('time', 0))
    }
    used_screenshots = []

    for testcase in root.findall('.//testcase'):
        summary['total'] += 1
        name = testcase.get('name')
        class_name = testcase.get('classname')
        time_spent = float(testcase.get('time', 0))

        result = {
            'name': name,
            'status': '✅ Passou',
            'details': '',
            'screenshot_data_uri': None,
            'time': f"{time_spent:.2f}s"
        }

        failure = testcase.find('failure')
        if failure is not None:
            summary['failed'] += 1
            result['status'] = '❌ Falhou'
            result['details'] = failure.text
            screenshot_abs = get_screenshot_path(name, class_name, execution_base, screenshot_sources)
            if screenshot_abs:
                data_uri = build_data_uri(screenshot_abs)
                if data_uri:
                    result['screenshot_data_uri'] = data_uri
                    used_screenshots.append(screenshot_abs)
        elif testcase.find('skipped') is not None:
            summary['skipped'] += 1
            result['status'] = '⚠️ Pulou'
        else:
            summary['passed'] += 1

        test_results_by_file.setdefault(class_name, []).append(result)

    return summary, test_results_by_file, used_screenshots


def generate_html_report(summary, results_by_file, html_output_file):
    """Gera o arquivo HTML final a partir dos dados processados."""
    tables = []
    for file_name, results in results_by_file.items():
        rows = []
        for res in results:
            screenshot_html = ''
            if res['screenshot_data_uri']:
                screenshot_html = (
                    '<h4>Screenshot:</h4>'
                    f'<img class="screenshot" src="{res["screenshot_data_uri"]}" alt="Screenshot">'
                )

            details_toggle = (
                '<span class="details-toggle" onclick="toggleDetails(this)">Mostrar</span>'
                if res['details'] else 'N/A'
            )

            row_html = f"""
                <tr>
                    <td>{res['name']}</td>
                    <td class="status-{res['status'].split(' ')[1].lower()}">{res['status']}</td>
                    <td>{res['time']}</td>
                    <td>
                        {details_toggle}
                        <div class="details-content">
                            <h4>Mensagem de Erro:</h4><pre>{res['details']}</pre>
                            {screenshot_html}
                        </div>
                    </td>
                </tr>
            """
            rows.append(row_html)

        table_html = f"""
        <h3>Arquivo: {file_name.replace('.', '/')}.py</h3>
        <table>
            <thead><tr><th>Teste</th><th>Status</th><th>Duração</th><th>Detalhes</th></tr></thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
        tables.append(table_html)

    tables_html = ''.join(tables)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Relatório de Testes</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; background-color: #f4f7f9; color: #333; }}
            .container {{ max-width: 1200px; margin: 20px auto; padding: 20px; background-color: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-radius: 8px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2, h3 {{ color: #2c3e50; }}
            h3 {{ margin-top: 30px; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
            .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .card {{ background-color: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
            .card .number {{ font-size: 2.5em; font-weight: bold; }}
            .card.passed .number {{ color: #2ecc71; }} .card.failed .number {{ color: #e74c3c; }} .card.total .number {{ color: #3498db; }} .card.duration .number {{ color: #f39c12; }}
            .card .label {{ font-size: 1em; color: #7f8c8d; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }} th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #34495e; color: #fff; }} tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .status-passou {{ color: #27ae60; font-weight: bold; }} .status-falhou {{ color: #c0392b; font-weight: bold; }} .status-pulou {{ color: #7f8c8d; font-weight: bold; }}
            .details-toggle {{ cursor: pointer; color: #3498db; text-decoration: underline; }}
            .details-content {{ display: none; background-color: #fdfdfd; padding: 15px; margin-top: 10px; border-left: 4px solid #3498db; }}
            .details-content pre {{ white-space: pre-wrap; word-wrap: break-word; background-color: #ecf0f1; padding: 10px; border-radius: 4px; }}
            .screenshot {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin-top: 10px; }}
            footer {{ text-align: center; margin-top: 20px; padding: 10px; font-size: 0.9em; color: #95a5a6; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relatório de Testes Automatizados</h1><p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <div class="summary">
                <div class="card total"><div class="number">{summary['total']}</div><div class="label">Total</div></div>
                <div class="card passed"><div class="number">{summary['passed']}</div><div class="label">Passaram</div></div>
                <div class="card failed"><div class="number">{summary['failed']}</div><div class="label">Falharam</div></div>
                <div class="card duration"><div class="number">{summary['duration']:.2f}s</div><div class="label">Duração</div></div>
            </div>
            <h2>Resultados Detalhados</h2>
            {tables_html}
        </div>
        <footer>Relatório gerado nativamente com Python.</footer>
        <script>
            function toggleDetails(element) {{
                const content = element.nextElementSibling;
                if (content.style.display === "block") {{ content.style.display = "none"; element.textContent = "Mostrar"; }}
                else {{ content.style.display = "block"; element.textContent = "Esconder"; }}
            }}
        </script>
    </body>
    </html>
    """
    with open(html_output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Relatório gerado com sucesso em: {html_output_file}")


def cleanup_screenshots(file_paths):
    """Remove os arquivos de screenshot utilizados e limpa diretórios vazios."""
    unique_files = sorted({os.path.abspath(path) for path in file_paths if path}, reverse=True)
    removed = 0

    for file_path in unique_files:
        try:
            os.remove(file_path)
            removed += 1
        except FileNotFoundError:
            continue
        except OSError as exc:
            print(f"Aviso: não foi possível remover {file_path}: {exc}")

    candidate_dirs = sorted({os.path.dirname(path) for path in unique_files}, key=len, reverse=True)
    for directory in candidate_dirs:
        try:
            if os.path.isdir(directory) and not os.listdir(directory):
                os.rmdir(directory)
        except OSError:
            continue

    return removed


def main(execution_path):
    """Função principal que recebe o caminho da execução."""
    execution_path = os.path.abspath(execution_path)
    xml_file = os.path.join(execution_path, 'report.xml')
    html_output_file = os.path.join(execution_path, 'relatorio_custom.html')

    if not os.path.exists(xml_file):
        print(f"Erro: Arquivo de resultados '{xml_file}' não encontrado.")
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    screenshot_sources = [
        os.path.join(execution_path, 'test-results'),
        os.path.join(execution_path, 'screenshots'),
        os.path.join(project_root, 'screenshots'),
    ]

    summary, results_by_file, used_screenshots = parse_test_results(xml_file, screenshot_sources, execution_path)
    generate_html_report(summary, results_by_file, html_output_file)
    removed = cleanup_screenshots(used_screenshots)
    if removed:
        print(f"Screenshots removidos após embutir no relatório: {removed}")

