# pages/proposta_page.py

import re
from playwright.sync_api import Page, FrameLocator, Locator, expect
from .base_page import BasePage


class PropostaPage(BasePage):
    """
    Page Object para a página de Proposta Comercial.
    """
    def __init__(self, page: Page):
        self.page = page
        # Localizadores da página principal
        self.caixa_busca: Locator = page.get_by_role("textbox", name="Procurar")
        self.menu_comercial: Locator = page.get_by_text("Comercial", exact=True)
        self.link_proposta_comercial: Locator = page.locator("a").filter(has_text="Proposta Comercial")
        
        # Localizador do Iframe principal da proposta
        self.frame_principal: FrameLocator = page.frame_locator('iframe[name="frame"]')
        
        # Localizadores dentro do Iframe
        self.input_cnpj: Locator = self.frame_principal.locator('input[name="txtCNPJ"]')
        self.input_nome_contato: Locator = self.frame_principal.locator('input[name="txtNome_Contato"]')
        self.select_ponto_operacao: Locator = self.frame_principal.locator('select[name="cboPonto_Operacao"]')
        self.select_tipo_proposta: Locator = self.frame_principal.locator('select[name="cboTipo_Proposta"]')
        self.select_servico_transporte: Locator = self.frame_principal.locator('select[name="cboTipoServicoTransporte"]')
        self.radio_tipo_cobranca: Locator = self.frame_principal.locator('input[name="optTipo_Cobranca_aux"]').nth(1)
        self.select_familia_produto: Locator = self.frame_principal.locator('select[name="txtFAMILIA_PRODUTO_ID"]')
        self.select_tipo_pagamento_frete: Locator = self.frame_principal.locator("#cboTAB_TIPO_PAGTO_FRETE_CLI")
        self.botao_gravar: Locator = self.frame_principal.get_by_role("button", name="Gravar")
        self.carga_perigosa_checkbox: Locator = self.frame_principal.locator("input[name='chkCarga_Perigosa']")
        
        # Localizador do Iframe aninhado para seleção de cliente/responsável
        self.frame_selecao_cliente: FrameLocator = self.frame_principal.frame_locator("#ISelGer")

        # --- Localizadores para novas funções ---

        # Links de Navegação (dentro do frame principal)
        self.link_servicos_agregados: Locator = self.frame_principal.get_by_role("link", name="Serviços Agregados")
        self.link_matriz_transporte: Locator = self.frame_principal.get_by_role("link", name="Matriz de Transporte")
        self.link_aceitacao: Locator = self.frame_principal.get_by_role("link", name="Aceitação")

        # Seção: Serviços Agregados
        self.radio_porta_a_porta: Locator = self.frame_principal.get_by_role("cell", name="Porta a Porta").locator("#optTipo_Modal")
        self.radio_porto_a_porto: Locator = self.frame_principal.get_by_role("cell", name="Porto a Porto").locator("#optTipo_Modal")
        self.radio_embarcador: Locator = self.frame_principal.get_by_role("cell", name="Embarcador").get_by_role("radio")
        self.radio_recebedor: Locator = self.frame_principal.get_by_role("cell", name="Recebedor").get_by_role("radio")
        self.input_valor_declarado: Locator = self.frame_principal.locator('input[name="txtVal_Declarado"]')
        self.radio_sem_ddr: Locator = self.frame_principal.get_by_role("cell", name="Sem DDR").get_by_role("radio")
        self.mensagem_servicos_agregados_sucesso: Locator = self.frame_principal.get_by_text("Serviços Agregados Gravados")

        # Seção: Matriz de Transporte
        self.input_municipio_origem: Locator = self.frame_principal.locator('input[name="txtMunicipio_Origem"]')
        self.input_municipio_destino: Locator = self.frame_principal.locator('input[name="txtMunicipio_Destino"]')
        self.select_porto_origem: Locator = self.frame_principal.locator("#cboPorto_Origem")
        self.select_porto_destino: Locator = self.frame_principal.locator("#cboPorto_Destino")
        self.select_tipo_container: Locator = self.frame_principal.locator('select[name="cboTab_Tipo_Container"]')
        self.input_peso_estimado: Locator = self.frame_principal.locator('input[name="txtPeso_Estimado"]')
        self.input_num_entregas: Locator = self.frame_principal.locator('input[name="txtNum_Entregas"]')
        self.input_num_coletas: Locator = self.frame_principal.locator('input[name="txtNum_Coletas"]')
        self.mensagem_matriz_sucesso: Locator = self.frame_principal.get_by_text("Proposta Origem/Destino Inclu")

        # Seção: Recalcular
        self.botao_recalcular: Locator = self.frame_principal.get_by_role("button", name="Recalcular")
        self.checkbox_trecho_0: Locator = self.frame_principal.locator("#chk_Trechos0")
        self.botao_voltar: Locator = self.frame_principal.get_by_role("button", name="Voltar")

        # Seção: Aceitação
        self.input_responsavel_cliente: Locator = self.frame_principal.locator('input[name="txtResponsavel_Cliente"]')
        self.input_qtde_containers: Locator = self.frame_principal.locator('input[name="txtQtde_Containers"]')
        self.botao_gravar_aceitacao: Locator = self.frame_principal.get_by_role("button", name="Gravar", exact=True)
        self.mensagem_aceitacao_sucesso: Locator = self.frame_principal.get_by_text("Gravação efetuada com sucesso")

    def _selecionar_item_no_iframe_de_busca(self, nome_item: str, timeout: int = 10000):
        try:
            celula_item = self.frame_selecao_cliente.get_by_role("cell", name=nome_item, exact=True).first
            self.esperar_estar_visivel(celula_item, timeout=timeout)
            self.clicar(celula_item)

        except Exception as e:
            print("não encontrou o item no iframe de busca")


    def marcar_carga_perigosa(self):
        self.clicar(self.carga_perigosa_checkbox)


    def navegar_para_proposta_comercial(self):
        self.digitar_caracteres(self.caixa_busca, "proposta", delay=100)
        self.clicar(self.menu_comercial)
        self.clicar(self.link_proposta_comercial)
        #esperar até o frame carregar
        self.esperar_estar_visivel(self.input_cnpj)


    def selecionar_cliente(self, cnpj: str, nome_cliente: str):
        """Preenche o CNPJ e seleciona o cliente na lista de resultados."""
        self.digitar_caracteres(self.input_cnpj, cnpj, delay=100)
        # Aguarda o cliente aparecer no iframe aninhado e clica nele
        self._selecionar_item_no_iframe_de_busca(nome_cliente)
        # Aguarda o campo CNPJ ser desabilitado, confirmando que o cliente foi carregado

        

    def preencher_dados_proposta(self, nome_contato: str, valor_ponto_operacao: str, valor_tipo_proposta: str, valor_servico_transporte: str, valor_familia_produto: str, valor_tipo_pagamento: str):
        self.digitar_caracteres(self.input_nome_contato, nome_contato, delay=100)
        self.selecionar_opcao(self.select_ponto_operacao, valor_ponto_operacao)
        self.selecionar_opcao(self.select_tipo_proposta, valor_tipo_proposta)
        self.selecionar_opcao(self.select_servico_transporte, valor_servico_transporte)
        self.marcar(self.radio_tipo_cobranca)
        self.selecionar_opcao(self.select_familia_produto, valor_familia_produto)
        self.selecionar_opcao(self.select_tipo_pagamento_frete, valor_tipo_pagamento)


    def salvar_proposta(self):
        self.page.wait_for_timeout(2000)
        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.obter_localizador_mensagem_sucesso())

    def obter_localizador_mensagem_sucesso(self) -> Locator:
        """Retorna o locator da mensagem de sucesso, procurando por uma tag <font> com texto iniciando em 'PC '."""
        # Localiza um elemento <font> cujo texto começa com "PC "
        return self.frame_principal.locator("font", has_text=re.compile(r"^PC\s"))

    def obter_numero_proposta(self) -> str:
        """Extrai o número da proposta da mensagem de sucesso."""
        locator_sucesso = self.obter_localizador_mensagem_sucesso()
        self.esperar_estar_visivel(locator_sucesso)
        texto_completo = self.obter_texto_interno(locator_sucesso)

        # Extrai o número da string "PC 123456 ..." usando split
        partes = texto_completo.split() # split() sem args lida melhor com múltiplos espaços
        if len(partes) > 1 and partes[0] == "PC":
            return partes[1]
        
        raise ValueError(f"Não foi possível extrair o número da proposta do texto: '{texto_completo}'")

    def preencher_servicos_agregados_PAxPA(self, valor_declarado: str):
        self.clicar(self.link_servicos_agregados)
        self.marcar(self.radio_porta_a_porta)
        self.marcar(self.radio_embarcador)
        self.marcar(self.radio_recebedor)
        self.preencher(self.input_valor_declarado, valor_declarado)
        self.marcar(self.radio_sem_ddr)
        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_servicos_agregados_sucesso)

    def preencher_servicos_agregados_POxPO(self):
        self.clicar(self.link_servicos_agregados)
        self.marcar(self.radio_porto_a_porto)
        self.page.wait_for_timeout(2000)

        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_servicos_agregados_sucesso)

    def preencher_servicos_agregados_POxPO_com_carga_perigosa(self):
        self.clicar(self.link_servicos_agregados)
        self.marcar(self.radio_porto_a_porto)
        self.page.wait_for_timeout(2000)
        self.marcar_carga_perigosa()

        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_servicos_agregados_sucesso) 

    def preencher_matriz_transporte_PAxPA(self, cidade_origem: str, nome_cidade_origem_lista: str, porto_origem_valor: str, cidade_destino: str, nome_cidade_destino_lista: str, porto_destino_valor: str, tipo_container_valor: str, peso_estimado: str, num_entregas: str, num_coletas: str):
        """Navega para 'Matriz de Transporte' e preenche os dados."""
        self.clicar(self.link_matriz_transporte)
        
        # Origem
        self.digitar_caracteres(self.input_municipio_origem, cidade_origem, delay=100)
        self._selecionar_item_no_iframe_de_busca(nome_cidade_origem_lista)
        self.selecionar_opcao(self.select_porto_origem, porto_origem_valor)
        # Destino
        self.digitar_caracteres(self.input_municipio_destino, cidade_destino    , delay=100)
        self._selecionar_item_no_iframe_de_busca(nome_cidade_destino_lista)
        self.selecionar_opcao(self.select_porto_destino, porto_destino_valor)
        # Dados do Transporte
        self.selecionar_opcao(self.select_tipo_container, tipo_container_valor)
        self.preencher(self.input_peso_estimado, peso_estimado)
        self.preencher(self.input_num_entregas, num_entregas)
        self.preencher(self.input_num_coletas, num_coletas)
        
        # Salvar
        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_matriz_sucesso)

    def preencher_matriz_transporte_POxPO(self, porto_origem_valor: str, porto_destino_valor: str, tipo_container_valor: str, peso_estimado: str, num_coletas: str):
        """Navega para 'Matriz de Transporte' e preenche os dados."""
        self.clicar(self.link_matriz_transporte)
        # Origem
        self.selecionar_opcao(self.select_porto_origem, porto_origem_valor)
        # Destino
        self.selecionar_opcao(self.select_porto_destino, porto_destino_valor)
        # Dados do Transporte
        self.selecionar_opcao(self.select_tipo_container, tipo_container_valor)
        self.preencher(self.input_peso_estimado, peso_estimado)
        self.preencher(self.input_num_coletas, num_coletas)

        # Salvar
        self.page.wait_for_timeout(2000)

        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_matriz_sucesso)

   
    def recalcular_proposta(self):
        self.clicar(self.botao_recalcular)
        self.esperar_estar_visivel(self.checkbox_trecho_0) # Aguarda o 1º cálculo
        self.marcar(self.checkbox_trecho_0)
        self.clicar(self.botao_recalcular)
        self.esperar_estar_visivel(self.botao_voltar) # Aguarda o 2º cálculo
        self.clicar(self.botao_voltar)

    def preencher_aceitacao(self, responsavel_busca: str, responsavel_lista: str, qtde_containers: str):
        self.clicar(self.link_aceitacao)
        self.digitar_caracteres(self.input_responsavel_cliente, responsavel_busca)
        self._selecionar_item_no_iframe_de_busca(responsavel_lista)
        self.digitar_caracteres(self.input_qtde_containers, qtde_containers)
        self.clicar(self.botao_gravar_aceitacao)
        self.esperar_estar_visivel(self.mensagem_aceitacao_sucesso)