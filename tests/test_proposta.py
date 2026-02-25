# tests/test_login.py

import pytest
import json

from playwright.sync_api import Page, expect
from pages.login_page_portal1 import LoginPage as login_portal1
from pages.proposta_page import PropostaPage
from pages.booking_page import BookingPage
from pages.login_page_portal2 import LoginPage as login_portal2
from pages.cargas_page import CargasPage
import random
import string


#preciso de uma funcao para ler o arquivo json com os dados da proposta
def carregar_dados_proposta():
    try:
        with open("dados.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}




@pytest.fixture(scope="session")
def dados_proposta():
    return carregar_dados_proposta()

#preciso salvar os dados_proposta em um arquivo json após cada teste
#e carregar os dados_proposta do arquivo json antes de cada teste
def salvar_dados_proposta(dados_proposta):
    with open("dados.json", "w", encoding="utf-8") as f:
        json.dump(dados_proposta, f, indent=4, ensure_ascii=False)

def gerar_string_aleatoria(tamanho=15):
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=tamanho))




def test_criar_booking_com_sucesso(page: Page, dados_proposta):
    # as credenciais são lidas diretamente das variáveis de ambiente pelo
    # objeto de página durante o login
    login_page = login_portal1(page)
    login_page.go_to()
    login_page.fazer_login()

    booking_page = BookingPage(page)

    # 1. Navega para a tela de criação de booking
    booking_page.navegar_pagina_booking()

    # 2. Preenche os dados do booking, usando a proposta do teste anterior
    numero_proposta = dados_proposta.get("numero_proposta")

    booking_page.preencher_dados_booking(
        proposta_comercial=numero_proposta,
        navio_viagem="EXEMPLO_Navio/VOYAGE",
        porto_origem="412",
        municipio_origem="8434",
        porto_destino="409",
        municipio_destino="617",
        tipo_container="55",
        qtde_containers="4"
    )

    # 3. Calcula, grava o booking e confirma a inclusão
    booking_page.calcular_e_gravar_proposta()
    print(booking_page.obter_numero_booking())
    dados_proposta["numero_booking"] = booking_page.obter_numero_booking()
    print(dados_proposta["numero_booking"])
    
    #salvar o dados_proposta em um arquivo json
    with open("dados.json", "w", encoding="utf-8") as f:
        json.dump(dados_proposta, f, indent=4, ensure_ascii=False)


   

def test_integracao_carga_com_sucesso(page: Page, dados_proposta):  

    login_page = login_portal2(page)
    login_page.go_to()
    login_page.fazer_login()

    cargas_page = CargasPage(page)
    
    cargas_page.acessar_pagina()
    cargas_page.clicar_botao_carga()
    cargas_page.preencher_numero_booking(dados_proposta['numero_booking'])

    cargas_page.clicar_botao_pesquisar()
    
    cargas_page.wait_for_integration()
    
    cargas_page.clicar_primeira_etapa()
    cargas_page.preencher_tipo_carga("carga geral")
    cargas_page.clicar_salvar_primeira_etapa()
    cargas_page.clicar_atualizar_carga()
    
    cargas_page.clicar_segunda_etapa()
    
    
    cargas_page.clicar_botao_edicao_manual_etapa_dois()
    cargas_page.clicar_botao_destinatario()
    cargas_page.preencher_razao_social_modal_pessoas("SAMPLE RECIPIENT")
    cargas_page.clicar_pesquisar_pessoas()
    cargas_page.selecionar_pessoa_edicao_manual('SAMPLE RECIPIENT')
    cargas_page.clicar_botao_pesquisar_container_modal_atualizar_pedido()
    cargas_page.clicar_adicionar_container_modal_atualizar_pedido()
    cargas_page.preencher_numero_container_input()
    cargas_page.preencher_tara_container('3880')
    cargas_page.clicar_pesquisar_tipo_container()

    cargas_page.preencher_codigo_integracao('55')
    cargas_page.clicar_pesquisar_tipos_container()
    cargas_page.selecionar_tipo_container('55')
    cargas_page.clicar_adicionar_container()
    cargas_page.preencher_tara_pedido('3880')
    cargas_page.preencher_primeiro_lacre(gerar_string_aleatoria(tamanho=15))
    cargas_page.preencher_segundo_lacre(gerar_string_aleatoria(tamanho=15))
    cargas_page.preencher_terceiro_lacre(gerar_string_aleatoria(tamanho=15))
    cargas_page.clicar_atualiza_pedido()
        
    cargas_page.clicar_adicionar()
    cargas_page.selecionar_tipo_documento('Outros')
    cargas_page.clicar_adicionar_nfe()

    cargas_page.preencher_descricao_nota('Teste automação Arthur')
    cargas_page.preencher_numero_nota(random.randint(1, 10000))
    cargas_page.preencher_valor_nota(round(random.uniform(1, 10000), 2))
    cargas_page.preencher_peso_nota(round(random.uniform(1, 10000), 2))
    cargas_page.clicar_destinatario_nota()
    cargas_page.preencher_razao_social_nota("SAMPLE RECIPIENT")

    cargas_page.clicar_pesquisar_nota()
    cargas_page.selecionar_pessoa_nota('SAMPLE RECIPIENT')
    cargas_page.clicar_adicionar_nota()

    cargas_page.clicar_fechar_nota()

    cargas_page.clicar_confirmar_envio_button()
    cargas_page.clicar_sim()
    
    cargas_page.clicar_terceira_etapa()
    cargas_page.clicar_ir_etapa_emissao()
    cargas_page.clicar_sim()
    #page.pause()






    
