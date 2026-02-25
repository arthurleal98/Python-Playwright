from .base_page import BasePage
from playwright.sync_api import Page, Locator

class BasePageMulti(BasePage):

    def __init__(self, page):
        super().__init__(page)
        self.processando_messenger: Locator = page.locator('//div[@class="blockUI blockMsg blockPage"]')
    
    
        
    def aguardar_mensagem_processando(self):
        try:
            # Primeiro, verifica rapidamente se apareceu
            if self.processando_messenger.is_visible(timeout=5000):
                # Se apareceu, espera desaparecer
                self.processando_messenger.wait_for(state="detached", timeout=200000)
        except :
            # Se não apareceu ou desapareceu rápido, continua sem erro
            pass    
        
    

    def obter_modal_atual(self, timeout: int = 10000) -> str:
        """
        Retorna o XPath do modal visível com o maior z-index.
        Aguarda até que pelo menos um modal esteja visível na tela.
        """
        # Espera até que pelo menos um modal apareça
        self.page.wait_for_selector("//div[contains(@class, 'modal fade show')]", timeout=timeout)

        modais = self.page.locator("//div[contains(@class, 'modal fade show')]")
        quantidade = modais.count()

        maior_z_index = -1
        index = 0

        for i in range(quantidade):
            modal_atual = self.page.locator(f"(//div[contains(@class, 'modal fade show')])[{i+1}]")

            # Aguarda o modal estar realmente visível/renderizado
            try:
                modal_atual.wait_for(state="visible", timeout=2000)
                z_index_atual = int(modal_atual.evaluate("el => parseInt(window.getComputedStyle(el).zIndex) || 0"))
            except Exception as e:
                print(f"Aviso: não foi possível obter z-index do modal {i+1}: {e}")
                continue

            if z_index_atual > maior_z_index:
                maior_z_index = z_index_atual
                index = i + 1

        return f"(//div[contains(@class, 'modal fade show')])[{index}]"
    
    def localizar_no_modal(self, seletor: str) -> Locator:
        """
        Localiza um elemento dentro do modal em foco.
        Exemplo: localizar_no_modal(".btn-primary") ou localizar_no_modal("input[name='razaoSocial']")
        """
        modal = self.obter_modal_atual()
        return self.page.locator(f"{modal}{seletor}")



    def clicar_no_elemento_no_modal(self, seletor: str):
        elemento = self.localizar_no_modal(seletor)
        elemento.click()

    def preencher_elemento_no_modal(self, seletor: str, valor: str):
        campo = self.localizar_no_modal(seletor)
        campo.fill(valor)


        
