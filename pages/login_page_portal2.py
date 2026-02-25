import os

from playwright.sync_api import Page, Locator, expect


from .base_page_multi import BasePageMulti
import os
from dotenv import load_dotenv

load_dotenv()

class LoginPage(BasePageMulti):
    def __init__(self, page: Page):
        super().__init__(page)
        self.base_url = os.getenv("PORTAL2_BASE_URL")
        if not self.base_url:
            raise RuntimeError("Define the environment variable PORTAL2_BASE_URL.")
        # Locators
        self.username_input: Locator = self.page.get_by_role("textbox", name="Email")
        self.password_input: Locator = self.page.get_by_role("textbox", name="Senha")
        self.login_button: Locator = self.page.get_by_role("button", name="Entrar")
        self.entrar_nsapp_button: Locator = self.page.get_by_role("button", name="Entrar com NsApps")
        # Locator para verificacao de login bem-sucedido
        self.main_menu: Locator = self.page.locator(".v-list.pt-0.v-list--dense.theme--light")

    def go_to(self):
        self.page.goto(self.base_url)

    def verificar_pagina_inicial(self):
        self.page.locator(
            "span.subheader-title",
            has_text="Seja bem-vindo"
        ).wait_for(state="visible", timeout=100000)
        

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
        """Executa o fluxo completo de login utilizando variáveis de ambiente genéricas."""
        self.preencher_usuario(os.getenv("TEST_USERNAME"))
        self.preencher_senha(os.getenv("TEST_PASSWORD"))
        self.clicar_login()
        self.verificar_pagina_inicial()

    def fazer_login_com_credenciais(self, username: str, password: str):
        """Executa o fluxo completo de login com credenciais fornecidas."""
        self.preencher_usuario(username)
        self.preencher_senha(password)
        self.clicar_login()

    

    def verificar_login_com_sucesso(self):
        """Verifica se o login foi bem-sucedido aguardando o menu principal ficar visivel."""
        self.esperar_estar_visivel(self.main_menu)
