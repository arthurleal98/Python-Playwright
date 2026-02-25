# Suíte de Testes End-to-End Automatizada (Playwright + Pytest)

## 📌 Visão Geral

Este repositório contém um exemplo de framework de testes end-to-end desenvolvido em **Python**, utilizando **Pytest** e **Playwright**.

O projeto demonstra:

- Uso do padrão **Page Object Model (POM)**
- Integração opcional com **SQL Server** para consultas de apoio
- Geração automática de **relatórios HTML**
- Captura automática de **screenshots em caso de falha**

> ⚠️ Observação: A versão original continha nomes de portais internos e credenciais de exemplo. Essas informações foram removidas ou substituídas por placeholders adequados para compartilhamento público. Não há código proprietário ou senhas reais neste repositório.

---

# ✅ Requisitos

- Python **3.11+** (com pip)
- Navegadores do Playwright:
  ```bash
  python -m playwright install
```

* **ODBC Driver 17 for SQL Server** (caso utilize acesso a banco via `pyodbc`)
* (Linux – opcional) Dependências adicionais:

  ```bash
  python -m playwright install-deps
  ```

---

# 🚀 Início Rápido

## 1️⃣ Criar e ativar ambiente virtual

```bash
python -m venv .venv
```

**Windows**

```bash
.\.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

---

## 2️⃣ Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3️⃣ Instalar navegadores do Playwright

```bash
python -m playwright install
```

---

## 4️⃣ Configurar variáveis de ambiente

Copie o arquivo:

```
.env.example
```

Para:

```
.env
```

Preencha com os dados reais do seu ambiente.

> ⚠️ Nunca versionar credenciais reais no repositório.

---

# 🔐 Variáveis de Ambiente (.env)

O projeto utiliza `python-dotenv` para carregar configurações no `conftest.py` e nas classes de página.

Exemplo de `.env`:

```env
# Credenciais utilizadas nos portais
TEST_USERNAME=seu_usuario
TEST_PASSWORD=sua_senha

# URLs base das aplicações
PORTAL1_BASE_URL=https://portal1.exemplo.com/
PORTAL2_BASE_URL=https://portal2.exemplo.com/

# Configuração opcional de banco de dados 1
DB1_DRIVER=ODBC Driver 17 for SQL Server
DB1_SERVER=
DB1_DATABASE=
DB1_USERNAME=
DB1_PASSWORD=
DB1_TRUST_SERVER_CERT=true
DB1_TRUSTED_CONNECTION=false

# Configuração opcional de banco de dados 2
DB2_DRIVER=ODBC Driver 17 for SQL Server
DB2_SERVER=
DB2_DATABASE=
DB2_USERNAME=
DB2_PASSWORD=
DB2_TRUST_SERVER_CERT=true
DB2_TRUSTED_CONNECTION=false
```

O arquivo `.env` está ignorado no `.gitignore`.

---

# 📁 Estrutura do Projeto

```
tests/                → Casos de teste Pytest (ex: test_proposta.py)
pages/                → Page Objects (interações com UI)
utils/                → Utilitários (ex: DatabaseClient para SQL Server)
dados.json            → Arquivo JSON para persistência de dados
screenshots/          → Capturas automáticas em caso de falha
execution_reports/    → Relatórios HTML gerados
allure-results/       → Resultados para geração de relatório Allure
```

---

# 🔄 Fluxo de Teste

O fluxo principal funciona da seguinte forma:

1. Login no primeiro portal.
2. Criação de um booking (dados carregados de `dados.json`).
3. Salvamento do número da proposta/booking no `dados.json`.
4. Login no segundo portal.
5. Integração de carga utilizando o booking previamente criado.

As classes de página encapsulam seletores e ações comuns, facilitando manutenção.

O utilitário de banco de dados pode ser usado para:

* Gerar dados de apoio
* Validar informações diretamente no banco

---

# ▶️ Execução dos Testes

## Executar via Pytest

Rodar toda a suíte:

```bash
pytest --headed
```

Executar apenas o fluxo de booking:

```bash
pytest tests/test_proposta.py --headed -k criar_booking
```

---

## Script Automatizado com Relatório

O script `run_and_report.py` executa os testes e gera relatório customizado:

```bash
python run_and_report.py
```

Executar teste específico:

```bash
python run_and_report.py tests/test_proposta.py::test_integracao_carga_com_sucesso
```

Os artefatos são gerados em:

```
execution_reports/
```

Incluindo:

* JUnit XML
* Dados brutos do Playwright
* Relatório HTML customizado

---

## Relatório Simplificado

O script `executar_teste.py` executa os testes utilizando `pytest-html` e aplica pós-processamento com `modificador_relatorio.py`.

---

# 📸 Evidências e Gerenciamento de Dados

* Screenshots são capturados automaticamente em caso de falha (ver `pytest_runtest_makereport` em `conftest.py`)
* `dados.json` armazena dados compartilhados entre execuções
* Para reiniciar completamente os testes, basta limpar ou remover o `dados.json`
* Para gerar relatório Allure:

```bash
allure serve allure-results
```

---

# 🛠️ Comandos Úteis

Atualizar Playwright:

```bash
pip install -U playwright
python -m playwright install
```

Instalar dependências Linux (CI):

```bash
python -m playwright install-deps
```

Executar testes em paralelo:

```bash
pytest -n auto
```

---

# 🧯 Solução de Problemas

**Erro de login**

* Verifique URLs e credenciais no `.env`

**Falha de conexão com banco**

* Verifique driver ODBC
* Parâmetros de conexão
* Firewall e acesso à rede

**Navegadores não encontrados**

* Execute novamente:

  ```bash
  python -m playwright install
  ```

**Execução interrompida após falha crítica**

* Limpe `__pycache__`
* Corrija o erro raiz
* Execute novamente

---

# 🤝 Contribuindo

1. Crie uma branch a partir da `main`
2. Adicione ou modifique testes seguindo o padrão **Page Object**
3. Execute `pytest` localmente
4. Garanta que os relatórios estejam sem falhas
5. Abra um Pull Request com descrição clara das alterações

Para adicionar novos fluxos, reutilize componentes existentes na pasta `pages/` para manter consistência e padronização.

---

# 📄 Licença

Este projeto está sob a licença **MIT**. Consulte o arquivo `LICENSE` para mais detalhes.
