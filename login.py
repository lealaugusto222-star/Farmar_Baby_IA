import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageChops
import os
import re

import banco


def email_valido(email):
    """Verifica o formato básico de um endereço de e-mail."""
    return re.fullmatch(r"[^@\s]+@(?:[^.@\s]+\.)+[^.@\s]+", email) is not None


def preparar_logo(caminho, altura_desejada):
    """Corta as margens em branco da imagem e devolve (imagem, largura, altura) na proporção certa"""
    imagem = Image.open(caminho).convert("RGBA")
    fundo = Image.new("RGBA", imagem.size, (255, 255, 255, 255))
    fundo.alpha_composite(imagem)
    imagem = fundo.convert("RGB")
    diferenca = ImageChops.difference(imagem, Image.new("RGB", imagem.size, (255, 255, 255)))
    caixa = diferenca.convert("L").point(lambda p: 255 if p > 15 else 0).getbbox()
    if caixa:
        imagem = imagem.crop(caixa)
    proporcao = imagem.width / imagem.height
    return imagem, int(altura_desejada * proporcao), altura_desejada


class TelaLogin:
    def __init__(self, master):
        self.master = master

        # Fundo suave para destacar o cartão de acesso.
        self.painel_principal = ctk.CTkFrame(
            self.master,
            fg_color="#f8fafc",
            corner_radius=0
        )
        self.painel_principal.pack(fill="both", expand=True)

        # Cartão central com largura consistente e conteúdo alinhado.
        self.conteudo_centro = ctk.CTkFrame(
            self.painel_principal,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#f1dce3",
            width=420,
        )
        self.conteudo_centro.pack(expand=True, padx=24, pady=24)

        # --- CARREGAR A LOGO ---
        caminho_atual = os.path.dirname(__file__)
        caminho_foto = os.path.join(caminho_atual, "foto_login.png")

        try:
            altura_logo = min(
                max(int(self.master.winfo_screenheight() * 0.18), 125),
                210,
            )
            imagem, largura, altura = preparar_logo(caminho_foto, altura_logo)
            self.imagem_logo = ctk.CTkImage(light_image=imagem, dark_image=imagem, size=(largura, altura))
            self.logo_label = ctk.CTkLabel(self.conteudo_centro, image=self.imagem_logo, text="")
            self.logo_label.pack(pady=(28, 8))
        except FileNotFoundError:
            ctk.CTkLabel(
                self.conteudo_centro,
                text="FARMAR BABY",
                font=("Arial", 22, "bold"),
                text_color="#ba4b6e",
            ).pack(pady=(32, 12))

        ctk.CTkLabel(
            self.conteudo_centro,
            text="Acesse sua conta",
            font=("Arial", 22, "bold"),
            text_color="#344054",
        ).pack(pady=(4, 4))
        ctk.CTkLabel(
            self.conteudo_centro,
            text="Entre para continuar seu acompanhamento",
            font=("Arial", 12),
            text_color="#667085",
        ).pack(pady=(0, 16))

        # --- SELETOR DE PERFIL (Gestante vs Profissional) ---
        self.perfil_selecionado = ctk.StringVar(value="Gestante")

        self.seletor_perfil = ctk.CTkSegmentedButton(
            self.conteudo_centro,
            values=["Gestante", "Profissional"],
            variable=self.perfil_selecionado,
            selected_color="#ff6b8b",
            selected_hover_color="#e05372",
            font=("Arial", 13, "bold"),
            width=320,
            height=35
        )
        self.seletor_perfil.pack(pady=(4, 14))

        # --- CAMPOS DE ENTRADA ---
        self.usuario = ctk.CTkEntry(
            self.conteudo_centro,
            width=320,
            height=42,
            placeholder_text="E-mail",
            fg_color="#f8fafc",
            border_color="#e2e8f0",
            border_width=1,
            corner_radius=10,
        )
        self.usuario.pack(pady=7)

        self.senha_mostrada = False
        self.linha_senha = ctk.CTkFrame(
            self.conteudo_centro,
            fg_color="transparent",
            width=320,
        )
        self.linha_senha.pack(pady=7)
        self.linha_senha.pack_propagate(False)
        self.linha_senha.configure(height=42)
        self.senha = ctk.CTkEntry(
            self.linha_senha,
            width=250,
            height=42,
            placeholder_text="Senha",
            show="*",
            fg_color="#f8fafc",
            border_color="#e2e8f0",
            border_width=1,
            corner_radius=10,
        )
        self.senha.pack(side="left", fill="x", expand=True)
        self.botao_mostrar_senha = ctk.CTkButton(
            self.linha_senha,
            width=64,
            height=42,
            text="Mostrar",
            font=("Arial", 11, "bold"),
            fg_color="#fce7ef",
            hover_color="#f7c9d8",
            text_color="#9f3f5e",
            corner_radius=10,
            command=self.alternar_visibilidade_senha,
        )
        self.botao_mostrar_senha.pack(side="right", padx=(6, 0))

        # Apertar Enter em qualquer campo também faz o login
        self.usuario.bind("<Return>", self._ao_pressionar_enter)
        self.senha.bind("<Return>", self._ao_pressionar_enter)

        # --- BOTÃO ENTRAR ---
        self.botao_entrar = ctk.CTkButton(
            self.conteudo_centro,
            width=320,
            height=45,
            text="Entrar",
            font=("Arial", 16, "bold"),
            fg_color="#ff6b8b",
            hover_color="#d94f70",
            corner_radius=10,
            command=self.validar_login
        )
        self.botao_entrar.pack(pady=(17, 12))

        # --- LINK PARA O CADASTRO ---
        self.link_cadastro = ctk.CTkButton(
            self.conteudo_centro,
            text="Ainda não tem uma conta? Cadastre-se",
            font=("Arial", 12, "underline"),
            fg_color="transparent",
            text_color="#ba4b6e",
            hover_color="#fce7ef",
            command=self.master.abrir_cadastro
        )
        self.link_cadastro.pack(pady=(4, 20))
        self.master.after(100, self.usuario.focus_set)

    def alternar_visibilidade_senha(self):
        self.senha_mostrada = not self.senha_mostrada
        self.senha.configure(show="" if self.senha_mostrada else "*")
        self.botao_mostrar_senha.configure(
            text="Ocultar" if self.senha_mostrada else "Mostrar"
        )

    def _ao_pressionar_enter(self, event):
        self.validar_login()
        return "break"

    def validar_login(self):
        email = self.usuario.get().strip()
        senha_digitada = self.senha.get()
        tipo_perfil = self.perfil_selecionado.get().lower()  # "gestante" ou "profissional"

        if not email or not senha_digitada:
            messagebox.showerror(
                "Dados incompletos",
                "Informe seu e-mail e sua senha para entrar.",
            )
            return

        if not email_valido(email):
            messagebox.showerror(
                "E-mail inválido",
                "Digite um endereço de e-mail válido.",
            )
            return

        # Confere no banco de dados (e-mail, senha e perfil escolhido)
        try:
            usuario = banco.validar_login(email, senha_digitada, tipo_perfil)
        except banco.ErroBanco as erro:
            messagebox.showerror("Falha no acesso", str(erro))
            return

        if usuario is None:
            messagebox.showerror(
                "Não foi possível entrar",
                "Confira seu e-mail, sua senha e o perfil selecionado.",
            )
            return

        if usuario["tipo"] == "gestante":
            self.master.abrir_dashboard(usuario)
        else:
            self.master.abrir_dashboard_profissional()