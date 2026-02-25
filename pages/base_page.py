# pages/base_page.py

from playwright.sync_api import Page, Locator, expect
from playwright.sync_api import FrameLocator

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://the-internet.herokuapp.com"
        self.frame_principal: FrameLocator = page.frame_locator('iframe[name="frame"]')

        self.carregamento_overlay: Locator = self.frame_principal.locator('#DivProgressbar')
        self.tela_bugada: Locator = self.page.get_by_role("heading", name="Nenhum favorito ainda")
        
    
    def recarregar_pagina(self):
        """Recarrega a página atual."""
        self.page.reload()

    def handle_bugged_screen(self):
        """Detecta e corrige telas que eventualmente ficam travadas/bugadas.

        O nome antigo referia-se a um portal específico; agora é genérico para
        evitar qualquer associação com produtos internos ao tornar o código
        público.
        """
        try:
            self.page.wait_for_timeout(10000)  # espera fixa opcional
            if self.tela_bugada.is_visible():
                self.recarregar_pagina()
        except Exception as e:
            print(f"Erro ao verificar tela bugada: {e}")

    def navigate(self, path: str):
        """Navega para uma URL completa construída a partir da base_url e do path."""
        self.page.goto(f"{path}")

    def get_title(self) -> str:
        """Retorna o título da página atual."""
        return self.page.title()

    def clicar(self, locator: Locator):
        """Clica em um elemento na página."""
        
        locator.click()

    def preencher(self, locator: Locator, texto: any):
        """Preenche um campo de entrada com texto (rápido)."""
        self.clicar(locator)
        locator.clear()

        locator.fill(str(texto))

    


    def esperar_carregar(self):
        """Espera até que o overlay de carregamento desapareça."""
        expect(self.carregamento_overlay).to_be_hidden(timeout=120000)

    def digitar_caracteres(self, locator: Locator, texto: str, delay: int = 50):
        locator.click()
        """Digita texto em um campo, simulando a digitação caractere por caractere."""
        locator.type(texto, delay=delay)
        # esperar até a pagina carregar os itens relacionados ao texto digitado

    def scroll_ate_elemento(self, locator: Locator):
        """Rola a página até um elemento específico."""
        locator.scroll_into_view_if_needed()

    def obter_texto_do_locator(self, locator: Locator) -> str:
        """Obtém o texto do elemento e de seus descendentes (textContent)."""
        return locator.text_content()
    
    def obter_texto_interno(self, locator: Locator) -> str:
        """Obtém o texto visível do elemento (innerText)."""
        return locator.inner_text()

    def selecionar_opcao(self, locator: Locator, valor: str):
        """Seleciona uma opção em um elemento <select> pelo valor."""
        # esperar até a pagina carregar os itens relacionados ao select
        locator.select_option(valor)

    def marcar(self, locator: Locator):
        """Marca um elemento (checkbox ou radio button)."""
        locator.check()

    def esperar_estar_visivel(self, locator: Locator, timeout: int = 20000):
        """Espera até que um elemento esteja visível."""
        expect(locator).to_be_visible(timeout=timeout)

    def texto_esta_visivel(self, locator: Locator) -> bool:
        """Verifica se o texto de um locator está visível na página."""
        try:
            expect(locator).to_be_visible(timeout=5000)
            return True
        except:
            return False


