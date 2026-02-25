#!/usr/bin/env python3
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime

import gerar_relatorio  # seu gerador de relatório

# --- Configurações ---
REPORTS_BASE_DIR = 'execution_reports'


def _handle_remove_readonly(func, path, exc_info):
    exc = exc_info[1]
    if not isinstance(exc, PermissionError):
        raise exc

    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except OSError as inner_exc:
        raise inner_exc


def prune_old_reports(base_dir, keep=10):
    """Mantém apenas os relatórios mais recentes."""
    try:
        entries = [
            os.path.join(base_dir, entry)
            for entry in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, entry))
        ]
    except FileNotFoundError:
        return []

    entries.sort(key=os.path.basename, reverse=True)
    removed = []

    for old_path in entries[keep:]:
        try:
            os.chmod(old_path, stat.S_IWRITE)
        except OSError:
            pass

        try:
            shutil.rmtree(old_path, onerror=_handle_remove_readonly)
            removed.append(old_path)
        except OSError as exc:
            print(f"Aviso: não foi possível remover {old_path!r}: {exc}")

    return removed


def run():
    """Orquestra todo o processo: cria pastas, executa testes e gera o relatório."""
    # Instala browsers e dependências (se necessário)
    try:
        subprocess.run([sys.executable, '-m', 'playwright', 'install'], check=True)
    except subprocess.CalledProcessError as e:
        print("Erro ao instalar browsers do Playwright:")
        print(e.stderr)
        sys.exit(1)

    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)

    # ID único para a execução
    execution_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    execution_path = os.path.join(REPORTS_BASE_DIR, execution_id)

    screenshots_path = os.path.join(execution_path, 'test-results')
    os.makedirs(screenshots_path, exist_ok=True)

    xml_path = os.path.join(execution_path, 'report.xml')

    print(f"--- Iniciando Execução de Teste ID: {execution_id} ---")
    print(f"Diretório de saída: {execution_path}")

    # --- Verifica se o usuário passou um arquivo específico ---
    test_target = sys.argv[1] if len(sys.argv) > 1 else None

    # --- Monta o comando do pytest ---
    pytest_command = [
        sys.executable,
        '-m', 'pytest',
        f'--junitxml={xml_path}',
        f'--screenshot=only-on-failure',
        f'--output={screenshots_path}',
        '--headed',
        '--tracing=on'
    ]

    # Se o usuário informou um teste específico, adiciona ele ao comando
    if test_target:
        pytest_command.append(test_target)

    print(f"\nExecutando comando: {' '.join(pytest_command)}\n")

    result = subprocess.run(pytest_command, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print("--- Erros do Pytest ---")
        print(result.stderr)
        print("-----------------------")

    print("\n--- Gerando Relatório HTML ---")
    try:
        gerar_relatorio.main(execution_path)
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o relatório: {e}")

    removed_reports = prune_old_reports(REPORTS_BASE_DIR, keep=10)
    if removed_reports:
        print("\n--- Limpando relatórios antigos ---")
        for removed_path in removed_reports:
            print(f"Removido: {os.path.basename(removed_path)}")

    print("\n--- Processo Concluído ---")
    print(f"Relatório final disponível em: {os.path.join(execution_path, 'relatorio_custom.html')}")


if __name__ == "__main__":
    run()
