import customtkinter as ctk
from tkinter import messagebox
import re

import banco
from ui_components import (
    IconEntry,
    PainelInstitucional,
    PasswordField,
    preparar_logo as _preparar_logo,
)


def email_valido(email):
    """Verifica o formato básico de um endereço de e-mail."""
    return re.fullmatch(r"[^@\s]+@(?:[^.@\s]+\.)+[^.@\s]+", email) is not None


def preparar_logo(caminho, altura_desejada):
    """Mantém a função disponível usando a implementação compartilhada."""
    return _preparar_logo(caminho, altura_desejada)


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

        self.painel_institucional = PainelInstitucional(
            self.painel_principal,
            mensagem=(
                "Um espaço de acolhimento e informação\n"
                "para acompanhar cada etapa da gestação."
            ),
        )
        self.painel_institucional.grid(row=0, column=0, sticky="nsew")

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

        self._focus_after_id = self.master.after(100, self.usuario.focus_set)

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
            self.master.abrir_dashboard_profissional(usuario)