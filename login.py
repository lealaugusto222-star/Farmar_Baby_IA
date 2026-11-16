import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageChops
import os
import re

import banco
from ui_components import IconEntry, PasswordField


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

        self.painel_principal = ctk.CTkFrame(
            self.master,
            fg_color="#f7f8fb",
            corner_radius=0,
        )
        self.painel_principal.pack(fill="both", expand=True)
        self.painel_principal.grid_rowconfigure(0, weight=1)
        self.painel_principal.grid_columnconfigure(
            0,
            weight=4,
            minsize=280,
        )
        self.painel_principal.grid_columnconfigure(
            1,
            weight=6,
            minsize=430,
        )

        self.painel_institucional = ctk.CTkFrame(
            self.painel_principal,
            fg_color="#f8eaf0",
            corner_radius=0,
        )
        self.painel_institucional.grid(row=0, column=0, sticky="nsew")
        self.painel_institucional.grid_columnconfigure(0, weight=1)
        self.painel_institucional.grid_rowconfigure(0, weight=1)
        self.painel_institucional.grid_rowconfigure(2, weight=1)

        institucional = ctk.CTkFrame(
            self.painel_institucional,
            fg_color="transparent",
        )
        institucional.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=24,
            pady=24,
        )
        institucional.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            institucional,
            text="CUIDADO QUE ACOLHE",
            font=("Arial", 10, "bold"),
            text_color="#9e536c",
        ).pack(pady=(0, 14))

        caminho_atual = os.path.dirname(__file__)
        caminho_foto = os.path.join(caminho_atual, "foto_login.png")
        try:
            altura_logo = min(
                max(int(self.master.winfo_screenheight() * 0.16), 135),
                185,
            )
            imagem, largura, altura = preparar_logo(caminho_foto, altura_logo)
            self.imagem_logo = ctk.CTkImage(
                light_image=imagem,
                dark_image=imagem,
                size=(largura, altura),
            )
            ctk.CTkLabel(
                institucional,
                image=self.imagem_logo,
                text="",
            ).pack(pady=(0, 12))
        except FileNotFoundError:
            ctk.CTkLabel(
                institucional,
                text="FARMAR BABY",
                font=("Arial", 22, "bold"),
                text_color="#b84f73",
            ).pack(pady=(12, 24))
        ctk.CTkLabel(
            institucional,
            text="Cuidando de quem\ngera o futuro.",
            font=("Arial", 21, "bold"),
            text_color="#284b67",
            justify="center",
        ).pack(pady=(4, 8))
        ctk.CTkLabel(
            institucional,
            text=(
                "Um espaço de acolhimento e informação\n"
                "para acompanhar cada etapa da gestação."
            ),
            font=("Arial", 12),
            text_color="#66758a",
            justify="center",
        ).pack()

        self.painel_formulario = ctk.CTkFrame(
            self.painel_principal,
            fg_color="#ffffff",
            corner_radius=0,
        )
        self.painel_formulario.grid(row=0, column=1, sticky="nsew")
        self.painel_formulario.grid_rowconfigure(0, weight=1)
        self.painel_formulario.grid_columnconfigure(0, weight=1)

        self.conteudo_centro = ctk.CTkFrame(
            self.painel_formulario,
            fg_color="transparent",
            width=380,
        )
        self.conteudo_centro.grid(row=0, column=0, padx=30, pady=24)
        self.conteudo_centro.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.conteudo_centro,
            text="Bem-vinda de volta",
            font=("Arial", 26, "bold"),
            text_color="#243447",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ctk.CTkLabel(
            self.conteudo_centro,
            text="Entre com seus dados para continuar.",
            font=("Arial", 13),
            text_color="#667085",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 22))

        self.perfil_selecionado = ctk.StringVar(value="Gestante")
        self.seletor_perfil = ctk.CTkSegmentedButton(
            self.conteudo_centro,
            values=["Gestante", "Profissional"],
            variable=self.perfil_selecionado,
            selected_color="#ff6b8b",
            selected_hover_color="#e05372",
            font=("Arial", 13, "bold"),
            width=360,
            height=40,
        )
        self.seletor_perfil.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 22),
        )

        ctk.CTkLabel(
            self.conteudo_centro,
            text="E-mail",
            font=("Arial", 12, "bold"),
            text_color="#344054",
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", pady=(0, 7))
        self.usuario = IconEntry(
            self.conteudo_centro,
            icon="envelope",
            placeholder_text="voce@exemplo.com",
            width=360,
            height=50,
        )
        self.usuario.grid(row=4, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            self.conteudo_centro,
            text="Senha",
            font=("Arial", 12, "bold"),
            text_color="#344054",
            anchor="w",
        ).grid(row=5, column=0, sticky="ew", pady=(0, 7))
        self.senha = PasswordField(
            self.conteudo_centro,
            width=360,
            height=50,
        )
        self.senha.grid(row=6, column=0, sticky="ew")

        self.usuario.bind("<Return>", self._ao_pressionar_enter)
        self.senha.bind("<Return>", self._ao_pressionar_enter)

        self.botao_entrar = ctk.CTkButton(
            self.conteudo_centro,
            height=48,
            text="Entrar",
            font=("Arial", 15, "bold"),
            fg_color="#c65378",
            hover_color="#a94365",
            corner_radius=12,
            command=self.validar_login,
        )
        self.botao_entrar.grid(
            row=7,
            column=0,
            sticky="ew",
            pady=(24, 12),
        )

        self.link_cadastro = ctk.CTkButton(
            self.conteudo_centro,
            text="Ainda não tem uma conta?  Criar cadastro",
            font=("Arial", 12, "bold"),
            fg_color="transparent",
            text_color="#a94365",
            hover_color="#fbeef3",
            command=self.master.abrir_cadastro,
        )
        self.link_cadastro.grid(row=8, column=0, pady=(0, 10))

        ctk.CTkLabel(
            self.conteudo_centro,
            text="Farmar Baby  •  Cuidado e informação",
            font=("Arial", 10),
            text_color="#98a2b3",
        ).grid(row=9, column=0, pady=(4, 0))

        self.master.after(100, self.usuario.focus_set)

    def alternar_visibilidade_senha(self):
        self.senha.toggle_visibility()

    def _ao_pressionar_enter(self, _event):
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