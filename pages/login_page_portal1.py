import os

from playwright.sync_api import Page, Locator, expect

from .base_page import BasePage

from dotenv import load_dotenv

load_dotenv()


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.base_url = os.getenv("PORTAL1_BASE_URL")
        if not self.base_url:
            raise RuntimeError("Define the environment variable PORTAL1_BASE_URL.")
        # Locators
        self.username_input: Locator = self.page.get_by_role("textbox", name="Email")
        self.password_input: Locator = self.page.get_by_role("textbox", name="Senha")
        self.login_button: Locator = self.page.get_by_role("button", name="Entrar")
        self.entrar_nsapp_button: Locator = self.page.get_by_role("button", name="Entrar com NsApps")
        # Locator para verificacao de login bem-sucedido
        self.main_menu: Locator = self.page.locator(".v-list.pt-0.v-list--dense.theme--light")

    def go_to(self):
        self.page.goto(self.base_url)

    def preencher_usuario(self, username: str):
        """Preenche o campo de usuario e pressiona Enter para possivel validacao."""
        self.preencher(self.username_input, username)
        self.username_input.press("Enter")

    def preencher_senha(self, password: str):
        """Preenche o campo de senha."""
        self.preencher(self.password_input, password)

    def clicar_login(self):
        """Clica no botao de login."""
        self.clicar(self.login_button)

    def clicar_entrar_nsapp(self):
        """Clica no botao 'Entrar com NsApps'."""
        self.clicar(self.entrar_nsapp_button)

    def fazer_login(self):
        """Executa o fluxo completo de login."""
        self.clicar_entrar_nsapp()
        self.preencher_usuario(os.getenv("TEST_USERNAME"))
        self.preencher_senha(os.getenv("TEST_PASSWORD"))
        self.clicar_login()
        # after login, try to recover from any weird frozen screen
        self.handle_bugged_screen()

    def verificar_login_com_sucesso(self):
        """Verifica se o login foi bem-sucedido aguardando o menu principal ficar visivel."""
        self.esperar_estar_visivel(self.main_menu)
