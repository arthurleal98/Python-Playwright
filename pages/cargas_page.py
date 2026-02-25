from .base_page_multi import BasePageMulti
from playwright.sync_api import Page, Locator, expect

from utils.utils import DatabaseClient

class CargasPage(BasePageMulti):
    def __init__(self, page):
        super().__init__(page)

        self.pesquisa_input: Locator = self.page.get_by_role("searchbox", name="Pesquisar um Formulário")
        self.cargas_button: Locator = self.page.locator('button[data-bind="click: ExibirFiltros.eventClick, id: ExibirFiltros.id"]')
        self.booking_input: Locator = self.page.get_by_role("textbox", name="Nº do Booking:")

        self.pesquisar_button_modal = '//button[@data-bind="click: Pesquisar.eventClick, attr : { id: Pesquisar.id }"]'
        self.atualizar_carga_button: Locator = self.page.get_by_role("button", name=" Atualizar as cargas")
        self.pesquisar_button: Locator = self.page.locator('(//button[@data-bind="click: Pesquisar.eventClick, attr: { id: Pesquisar.id}"])[1]')
        self.selecionar_link = '//a[normalize-space(.)=\'Selecionar\']'
        self.descricao_input = '//input[@data-bind="value: Descricao.val, enable: true, valueUpdate: \'afterkeydown\', attr: { \'aria-label\': Descricao.text, maxlength: Descricao.maxlength, id: Descricao.id, name: Descricao.id }"]'
        self.primeira_etapa_button: Locator = self.page.locator("#tabTMS").first
        self.tipo_carga_input:Locator = self.page.get_by_role("textbox", name="*Tipo de Carga:").first
        self.salvar_primeira_etapa_button:Locator = self.page.locator('button[data-bind="attr: { id: SalvarDadosTransporte.id}, enable: SalvarDadosTransporte.enable,click: SalvarDadosTransporte.eventClick, visible: SalvarDadosTransporte.visible"]')
        self.salvar_button: Locator = self.page.get_by_role("button", name="Salvar")

        

        self.segunda_etapa_button: Locator = self.page.locator('//li[@data-bind="visible : EtapaNotaFiscal.visible"]').first
        self.editar_manualmente_etapa_dois_button: Locator = self.page.locator('//button[@onclick="EditarPedidoAdicionadoManualmente(event, 0)"]')
        
        
        # Modal Atualizar pedido
        self.atualizar_pedido_modal: Locator  = self.page.locator('#knoutModalAdicionarPedidoVinculado')
        self.destinatario_atualizar_pedido_button: Locator = self.atualizar_pedido_modal.locator('//button[@data-bind="attr: { id: Destinatario.idBtnSearch}"]')

        self.container_pesquisa_button: Locator = self.atualizar_pedido_modal.locator('//*[@data-bind="attr: { id: Container.idBtnSearch}, enable: Container.enable"]')
        
        
        # Modal Pesquisar Pessoas que fica dentro do Modal Atualizar pedido
        
        self.razao_social_pesquisar_pessoas_input: Locator = self.page.locator('//*[@data-bind="value: Nome.val, enable: true, valueUpdate: \'afterkeydown\', attr: { \'aria-label\': Nome.text, maxlength: Nome.maxlength, id: Nome.id, name: Nome.id }"]')
        self.pesquisa_cidade_pesquisar_pessoas_button: Locator = self.page.locator('//button[@data-bind="attr: { id: Localidade.idBtnSearch }"]')
        self.pesquisar_pessoas_button: Locator = self.page.locator('//div[@class="modal-content"][div[h4[normalize-space(.)=\'Pesquisar Pessoas\']]]//*[@data-bind="click: Pesquisar.eventClick, attr : { id: Pesquisar.id }"]')
        self.primeiro_selecionar_link: Locator = self.page.locator("//a[normalize-space(text())='Selecionar']").first
        #   

        self.adicionar_novo_container_button: Locator = self.page.locator('//*[@data-bind="click: AdicionarContainer.eventClick, attr : { id: AdicionarContainer.id }"]')
        self.numero_container_input: Locator = self.page.locator('//*[@data-bind="value: Numero.val, valueUpdate: \'afterkeydown\', attr: { maxlength: Numero.maxlength, id : Numero.id}"]')

        self.tara_container_input: Locator = self.page.locator('//*[@data-bind="value: Tara.val, valueUpdate: \'afterkeydown\', attr: { maxlength: Tara.maxlength, id : Tara.id}"]')
        self.tipo_container_pesquisa_button: Locator = self.page.locator('//*[@data-bind="attr: { id: TipoContainer.idBtnSearch}"]')
        self.descricao_tipo_container_input ='//*[@data-bind="value: Descricao.val, enable: true, valueUpdate: \'afterkeydown\', attr: { \'aria-label\': Descricao.text, maxlength: Descricao.maxlength, id: Descricao.id, name: Descricao.id }"]'
        self.codigo_integracao_input = '//*[@data-bind="value: CodigoIntegracao.val, enable: true, valueUpdate: \'afterkeydown\', attr: { \'aria-label\': CodigoIntegracao.text, maxlength: CodigoIntegracao.maxlength, id: CodigoIntegracao.id, name: CodigoIntegracao.id }"]'
        self.pesquisar_tipos_container_button: Locator = self.page.locator('//div[@class="modal-content"][div[contains(normalize-space(.), \'Busca de Tipos de Container\')]]//button[@data-bind="click: Pesquisar.eventClick, attr : { id: Pesquisar.id }"]')
        self.adicionar_container_button = '//*[@data-bind="click: Adicionar.eventClick, visible: Adicionar.visible, text: Adicionar.text, attr: { id : Adicionar.id}"]'
        self.tara_pedido_input = '//*[@data-bind="value: TaraContainer.val, valueUpdate: \'afterkeydown\', attr: { maxlength: TaraContainer.maxlength, id : TaraContainer.id}"]'
        self.primeiro_lacre_input = '//*[@data-bind="value: LacreContainerUm.val, enable: LacreContainerUm.enable, valueUpdate: \'afterkeydown\', attr: { maxlength: LacreContainerUm.maxlength, id : LacreContainerUm.id}"]'
        self.segundo_lacre_input = '//*[@data-bind="value: LacreContainerDois.val, enable: LacreContainerDois.enable, valueUpdate: \'afterkeydown\', attr: { maxlength: LacreContainerDois.maxlength, id : LacreContainerDois.id}"]'
        self.terceiro_lacre_input = '//*[@data-bind="value: LacreContainerTres.val, enable: LacreContainerTres.enable, valueUpdate: \'afterkeydown\', attr: { maxlength: LacreContainerTres.maxlength, id : LacreContainerTres.id}"]'
        self.atualizar_pedido_button = '//*[@data-bind="click: Adicionar.eventClick, visible: Adicionar.visible, enable: Adicionar.enable, text: Adicionar.text, attr: { id : Adicionar.id}"]'

        self.adicionar_button: Locator = self.page.locator('//*[@data-bind="click: ExibirMais.eventClick, enable: Pedido.enable, visible: ExibirMais.visible, attr: { value: ExibirMais.text, id : ExibirMais.id}"]')
    
        self.tipo_documento_select: Locator = self.page.locator('//*[@data-bind="options: TipoDocumento.options, optionsText: \'text\', optionsValue: \'value\', value: TipoDocumento.val, attr: { id : TipoDocumento.id}, event: {change: TipoDocumento.eventChange}, enable: Pedido.enable"]')
        self.adicionar_nfe_button: Locator =  self.page.locator('(//*[@data-bind="click: Adicionar.eventClick, visible: Adicionar.visible, enable: Adicionar.enable, text: Adicionar.text, attr: { id : Adicionar.id}"])[1]')
    
        self.descricao_nota_fiscal_input = '//*[@data-bind="css: Descricao.requiredClass, value: Descricao.val, attr: { maxlength: Descricao.maxlength, id : Descricao.id}, enable: Descricao.enable"]'
        self.numero_nota_input: Locator = self.page.locator('(//*[@data-bind="css: Numero.requiredClass, value: Numero.val, attr: { maxlength: Numero.maxlength, id : Numero.id}, enable: Numero.enable"])')
        self.valor_nota_input: Locator = self.page.locator('(//*[@data-bind="value: Valor.val, attr: { maxlength: Valor.maxlength, id : Valor.id}, enable: Valor.enable"])')
        self.peso_nota_input: Locator = self.page.locator('(//*[@data-bind="css: Peso.requiredClass, value: Peso.val, attr: { maxlength: Peso.maxlength, id : Peso.id}, enable: Peso.enable"])')
        self.razao_social_nota_input = '//*[@data-bind="value: Nome.val, enable: true, valueUpdate: \'afterkeydown\', attr: { \'aria-label\': Nome.text, maxlength: Nome.maxlength, id: Nome.id, name: Nome.id }"]'
        self.destinatario_nota_button = '//*[@data-bind="attr: { id: Destinatario.idBtnSearch}, enable: Destinatario.enable"]'
        self.adicionar_nota_button = '//*[@data-bind="click: Adicionar.eventClick, visible: Adicionar.visible, enable: Adicionar.enable, text: Adicionar.text, attr: { id : Adicionar.id}"]'
        self.fechar_nota_button: Locator = self.page.locator('//div[@id=\'divModalAdicionarNotasCarga\']//button[@class="btn-close"]')
        self.confirmar_envio_button: Locator = self.page.locator('//button[@data-bind="visible: (ConfirmarEnvioDocumentos.visible() && Pedido.enable()), attr: { id: ConfirmarEnvioDocumentos.id}, enable: ConfirmarEnvioDocumentos.enable, click: ConfirmarEnvioDocumentos.eventClick"]')
        self.pesquisar_nota_button = '//*[@data-bind="click: Pesquisar.eventClick, attr : { id: Pesquisar.id }"]'
        self.sim_button: Locator = self.page.get_by_role("button", name="Sim")

        self.titulo_nota_modal: Locator = self.page.locator('//*[@id="TituloNotasCarga"]')

        self.terceira_etapa_button: Locator = self.page.locator('//*[@data-bind="attr: {id : EtapaFreteTMS.idTab }, click : EtapaFreteTMS.eventClick"]').first
        self.ir_etapa_emissao_button: Locator = self.page.locator('(//*[@data-bind="attr: { id: AutorizarEmissaoDocumentos.id}, enable: AutorizarEmissaoDocumentos.enable, visible:  AutorizarEmissaoDocumentos.visibleBTN, click: AutorizarEmissaoDocumentos.eventClick"])[1]')


        
    def clicar_ir_etapa_emissao(self):
        self.clicar(self.ir_etapa_emissao_button)

    def clicar_terceira_etapa(self):
        self.clicar(self.terceira_etapa_button)


    def clicar_sim(self):
        self.clicar(self.sim_button)

    def clicar_pesquisar_nota(self):
        self.clicar_no_elemento_no_modal(self.pesquisar_nota_button)

    def clicar_confirmar_envio_button(self):
        self.clicar(self.confirmar_envio_button)
    
    def clicar_fechar_nota(self):
        self.clicar(self.fechar_nota_button)

    def clicar_adicionar_nota(self):
        self.clicar_no_elemento_no_modal(self.adicionar_nota_button)
    
    def selecionar_pessoa_edicao_manual(self, razao_social: str):
        self.clicar(self.page.locator(f"(//tr[1][td[2]//span[contains(normalize-space(.), '{razao_social}')]]/td[last()])[1]"))

    def selecionar_pessoa_nota(self, razao_social: str):
        self.clicar(self.page.locator(f"(//tr[1][td[2]//span[contains(normalize-space(.), '{razao_social}')]]/td[last()])[2]"))
    
    def preencher_razao_social_nota(self, nome:str):
        self.preencher_elemento_no_modal(self.razao_social_nota_input, nome)

    

    def clicar_destinatario_nota(self):
        self.clicar_no_elemento_no_modal(self.destinatario_nota_button)

    def preencher_peso_nota(self, peso:float):
        self.preencher(self.peso_nota_input, str(peso))
        self.clicar(self.titulo_nota_modal)
        self.clicar(self.peso_nota_input)
    def preencher_valor_nota(self, valor:float):
        self.preencher(self.valor_nota_input, str(valor))
        self.clicar(self.titulo_nota_modal)
        self.clicar(self.valor_nota_input)
    def preencher_numero_nota(self, numero:int):
        self.preencher(self.numero_nota_input, str(numero))
        self.clicar(self.titulo_nota_modal)
        self.clicar(self.numero_nota_input)

    def preencher_descricao_nota(self, texto:str):
        self.preencher_elemento_no_modal(self.descricao_nota_fiscal_input,texto)
        

    def clicar_adicionar_nfe(self):
        self.clicar(self.adicionar_nfe_button)
    
    def selecionar_tipo_documento(self, tipo: str):

        self.selecionar_opcao(self.tipo_documento_select, tipo)

    def clicar_adicionar(self):
        self.clicar(self.adicionar_button)

    def clicar_atualiza_pedido(self):
        self.clicar_no_elemento_no_modal(self.atualizar_pedido_button)
    
    def preencher_terceiro_lacre(self, lacre: str):
        self.preencher_elemento_no_modal(self.terceiro_lacre_input, lacre)

    def preencher_segundo_lacre(self, lacre: str):
        self.preencher_elemento_no_modal(self.segundo_lacre_input,lacre)
    
    def preencher_primeiro_lacre(self, lacre:str):
        self.preencher_elemento_no_modal(self.primeiro_lacre_input, lacre)


    def preencher_tara_pedido(self, tara:str):
        self.preencher_elemento_no_modal(self.tara_pedido_input, tara)

    def clicar_adicionar_container(self):
        self.clicar_no_elemento_no_modal(self.adicionar_container_button)        

    def selecionar_tipo_container(self, codigo:str):
        self.clicar(self.page.locator(f"//tr[td[normalize-space()='{codigo}']]//a[normalize-space(text())='Selecionar']"))

    def clicar_pesquisar_tipos_container(self):
        self.clicar(self.pesquisar_tipos_container_button)
    
    def preencher_codigo_integracao(self, codigo: str):
        self.preencher_elemento_no_modal(self.codigo_integracao_input, codigo)

    def preencher_descricao_tipo_container(self, descricao:str):
        self.preencher_elemento_no_modal(self.descricao_tipo_container_input, descricao)

    def clicar_pesquisar_tipo_container(self):
        self.clicar(self.tipo_container_pesquisa_button)

    def preencher_tara_container(self, tara:str):
        self.preencher(self.tara_container_input, tara)

    def preencher_numero_container_input(self):
        container = DatabaseClient.buscar_primeiro_container_valido(batch_size=50)
        if container:
            self.preencher(self.numero_container_input, container)

        

    def clicar_adicionar_container_modal_atualizar_pedido(self):
        self.clicar(self.adicionar_novo_container_button)

    def clicar_botao_pesquisar_container_modal_atualizar_pedido(self):
        self.clicar(self.container_pesquisa_button)



    def clicar_primeiro_selecionar(self):
        self.clicar(self.primeiro_selecionar_link)
    def clicar_pesquisar_pessoas(self):
        self.clicar(self.pesquisar_pessoas_button)

    def preencher_razao_social_modal_pessoas(self, razao:str):
        self.preencher(self.razao_social_pesquisar_pessoas_input, razao)

    def clicar_botao_destinatario(self):
        self.clicar(self.destinatario_atualizar_pedido_button)


    def clicar_botao_edicao_manual_etapa_dois(self):
        self.clicar(self.editar_manualmente_etapa_dois_button)

    def clicar_botao_pesquisar(self):
        self.clicar(self.pesquisar_button)

    def preencher_tipo_carga(self, nome:str):
        self.tipo_carga_input.clear()
        self.tipo_carga_input.press("Tab")
        self.preencher_elemento_no_modal(self.descricao_input, nome)
        self.clicar_no_elemento_no_modal(self.pesquisar_button_modal)
        self.clicar_no_elemento_no_modal(self.selecionar_link)

  

    def clicar_salvar_primeira_etapa(self):
        self.clicar(self.salvar_button)

    def clicar_segunda_etapa(self):
        self.clicar(self.segunda_etapa_button)

    def clicar_atualizar_carga(self):
        self.clicar(self.atualizar_carga_button)

    def wait_for_integration(self):
        """Waits for the background integration to complete.

        The original implementation polled a button for visibility, retrying up
        to ten times with one‑minute intervals. The name referenced a specific
        service; here it is kept generic.
        """
        for _ in range(10):
            try:
                expect(self.primeira_etapa_button).to_be_visible(timeout=60000)
                return
            except:
                self.clicar_atualizar_carga()

        raise Exception("Maximum wait time for integration exceeded.")

    def clicar_primeira_etapa(self):
        self.clicar(self.primeira_etapa_button)

    def preencher_numero_booking(self, numero:str):
        self.preencher(self.booking_input, numero)
    
    def clicar_botao_carga(self): 
        self.clicar(self.cargas_button)

    def preencher_pesquisar(self, nome:str):
        self.preencher(self.pesquisa_input, nome)
        self.pesquisa_input.press("Enter")

    def acessar_pagina(self):
        # use the base_url provided by the environment and append the relative
        # path for the cargasscreen; avoid hard‑coded domains
        self.navigate(f"{self.base_url}#Cargas/Carga")
        self.aguardar_mensagem_processando()
        expect(self.page.get_by_role("listitem").filter(has_text="Primeiro")).to_be_attached(timeout=60000)
