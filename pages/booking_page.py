import re
from playwright.sync_api import Page, FrameLocator, Locator, expect
from .base_page import BasePage

class BookingPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        self.caixa_busca: Locator = page.get_by_role("textbox", name="Procurar")
        self.menu_customer_service: Locator = page.get_by_text("Customer Service", exact=True)
        self.opcao_menu_busca: Locator = page.locator("a").filter(has_text=re.compile(r"^Booking$"))

        self.frame_principal: FrameLocator = page.frame_locator('iframe[name="frame"]')

        self.frame_selecao_cliente: FrameLocator = self.frame_principal.frame_locator("#ISelGer")


        self.campo_proposta_comercial: Locator = self.frame_principal.locator('input[name="txtTPC_Id_Sistema_Externo"]')
        self.input_cnpj_embarcador: Locator = self.frame_principal.locator("input[name=\"txtcgc_embarcador\"]")
        self.campo_navio_viagem: Locator = self.frame_principal.locator('input[name="txtdesc_viagem_navio"]')
        self.select_porto_origem: Locator = self.frame_principal.locator("select[name=\"txtporto_origem_id\"]")
        self.selec_municipio_origem: Locator = self.frame_principal.locator("select[name=\"txtTerminalCheioOrigemID\"]")
        self.select_porto_destino: Locator = self.frame_principal.locator("select[name=\"txtporto_destino_id\"]")
        self.select_municipio_destino: Locator = self.frame_principal.locator("select[name=\"txtTerminalCheioDestinoID\"]")
        self.select_tipo_container: Locator = self.frame_principal.locator("select[name=\"txttab_tipo_container_id\"]")
        self.input_qtde_containers: Locator = self.frame_principal.locator("input[name=\"txtqtde_container\"]")

        self.botao_calcular: Locator = self.frame_principal.get_by_role("button", name="Calcular")
        self.botao_pesquisar: Locator = self.frame_principal.get_by_role("button", name="Pesquisar")
        self.botao_gravar: Locator = self.frame_principal.get_by_role("button", name="Gravar")
        self.botao_voltar: Locator = self.frame_principal.locator("button[name=\"Voltar\"]")
        self.link_agendamento: Locator = self.frame_principal.get_by_role("link", name="Agendamento")
        self.link_grade_horarios: Locator = self.frame_principal.get_by_text("Grade de Horários p/ Coleta")
        self.link_pesquisa_booking: Locator = self.frame_principal.get_by_role("link", name="Pesquisa")

        self.input_data_inicio: Locator = self.frame_principal.locator("input[name=\"txtData0\"]")
        self.input_hora: Locator = self.frame_principal.locator("input[name=\"txtHora0\"]")
        self.botao_copiar: Locator = self.frame_principal.locator("button[name=\"Copiar 1ª Linha\"]")

        self.input_numero_booking: Locator = self.frame_principal.locator("input[name=\"txtColuna1\"]")

        # Locators para fluxo de criação de booking
        self.mensagem_inclusao_sucesso: Locator = self.frame_principal.get_by_text("Inclusão do booking realizada")
        self.texto_agendamento_coleta: Locator = self.frame_principal.get_by_text("Agendamento de Coleta FCL")
        self.texto_agendamentos_container: Locator = self.frame_principal.get_by_text("Agendamentos de Container")

        self.carregamento_overlay: Locator = self.frame_principal.locator('#DivProgressbar')

        self.numero_booking: Locator = self.frame_principal.locator('input[name="txtnum_booking"]')

        self.primeiro_booking_pesquisa: Locator = self.frame_principal.locator('a[href^="BOOKINGCAD.ASP?BOOKING_ID="]')


    def esperar_carregar(self):
        """Espera até que o overlay de carregamento desapareça."""
        expect(self.carregamento_overlay).to_be_hidden(timeout=120000)


    def _selecionar_item_no_iframe_de_busca(self, nome_item: str, timeout: int = 10000):
            try:
                celula_item = self.frame_selecao_cliente.get_by_role("cell", name=nome_item, exact=True).first
                self.esperar_estar_visivel(celula_item, timeout=timeout)
                self.clicar(celula_item)
                self.esperar_carregar()


            except Exception as e:
                print("não encontrou o item no iframe de busca")

    def navegar_pagina_booking(self):
        self.recarregar_pagina()
        self.clicar(self.caixa_busca)
        self.digitar_caracteres(self.caixa_busca, "booking", delay=100)
        self.clicar(self.menu_customer_service)
        self.clicar(self.opcao_menu_busca)
        self.esperar_estar_visivel(self.campo_proposta_comercial)

    def selecionar_cnpj_embarcador(self, cnpj: str):
        self.digitar_caracteres(self.input_cnpj_embarcador, cnpj, delay=100)
        self._selecionar_item_no_iframe_de_busca(cnpj)

    def aguardar_valor_carregar_input_cnpj(self):
        expect(self.input_cnpj_embarcador).to_have_value(re.compile(r"^\d{14}$"), timeout=60000)

    def aguardar_opcoes_carregar_opcao_porto_origem(self):
        # precisa ter pelo menos 2 opções (a primeira é sempre vazia)
        expect(self.select_porto_origem.locator("option")).to_have_count(re.compile(r"^\d+$"), timeout=60000)

    def aguardar_opcoes_carregar_opcao_porto_destino(self):
        expect(self.select_porto_destino.locator("option")).to_have_count(re.compile(r"^\d+$"), timeout=60000)
    
    
    def preencher_dados_booking(self, proposta_comercial: str, navio_viagem: str, porto_origem: str, municipio_origem: str,
                               porto_destino: str, municipio_destino: str, tipo_container: str,
                               qtde_containers: str):
        #self.page.pause()
        
        self.digitar_caracteres(self.campo_proposta_comercial, proposta_comercial, delay=50)
        self.aguardar_valor_carregar_input_cnpj()
        self.digitar_caracteres(self.campo_navio_viagem, navio_viagem, delay=100)
        self.selecionar_opcao(self.select_porto_origem, porto_origem)
        self.selecionar_opcao(self.selec_municipio_origem, municipio_origem)
        self.selecionar_opcao(self.select_porto_destino, porto_destino)
        self.selecionar_opcao(self.select_municipio_destino, municipio_destino)
        self.selecionar_opcao(self.select_tipo_container, tipo_container)
        # agurdar 5 segundos para garantir que o select foi processado
        self.page.wait_for_timeout(5000)
        self.digitar_caracteres(self.input_qtde_containers, qtde_containers, delay=50)

    def calcular_e_gravar_proposta(self):
        self.clicar(self.botao_calcular)
        # esperar dois segundos para garantir que o cálculo foi processado
        self.page.wait_for_timeout(2000)
        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_inclusao_sucesso)
        self.clicar(self.mensagem_inclusao_sucesso)
        
    def acessar_agendamento(self):
        self.clicar(self.link_agendamento)

    def voltar_para_proposta(self):
        self.clicar(self.botao_voltar)
        self.esperar_estar_visivel(self.botao_gravar)

    def acessar_grade_horarios(self):
        self.page.pause()
        self.clicar(self.link_grade_horarios)
        self.esperar_estar_visivel(self.input_data_inicio)

    def clicar_item_por_texto(self, texto_item: str):
        """Clica em um item na página (link ou botão) identificado pelo texto."""
        item = self.frame_principal.get_by_text(texto_item, exact=True)
        self.clicar(item)

    def gravar_agendamento(self):
        """Clica no botão 'Gravar' na tela de agendamento e confirma."""
        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.texto_agendamento_coleta)
        self.clicar(self.texto_agendamento_coleta)

    def obter_numero_booking(self) -> str:
        """Retorna o número do booking atual."""
        return self.numero_booking.input_value()
    def preencher_e_gravar_grade_horarios(self):
        #digitar a data atual no formato dd/mm/yyyy
        from datetime import datetime
        data_atual = datetime.now().strftime("%d/%m/%Y")
        self.page.pause()
        self.digitar_caracteres(self.input_data_inicio, data_atual, delay=50)
        self.digitar_caracteres(self.input_hora, "08:00", delay=50)

        self.clicar(self.botao_copiar)
        self.clicar(self.botao_gravar)
        self.page.pause()
        self.esperar_estar_visivel(self.texto_agendamentos_container)
        self.clicar(self.texto_agendamentos_container)

    def clicar_gravar(self):
        self.clicar(self.botao_gravar)
        self.esperar_estar_visivel(self.mensagem_inclusao_sucesso)
        
    def acessar_pesquisa_booking(self):
        self.clicar(self.link_pesquisa_booking)
        self.esperar_estar_visivel(self.input_numero_booking)

    def preencher_numero_booking(self, numero_booking: str):
        self.digitar_caracteres(self.input_numero_booking, numero_booking, delay=50)
    
    def clicar_pesquisar(self):
        self.clicar(self.botao_pesquisar)

    def clicar_primeiro_resultado_pesquisa(self):
        self.clicar(self.primeiro_booking_pesquisa)
        self.esperar_estar_visivel(self.botao_gravar)
    

