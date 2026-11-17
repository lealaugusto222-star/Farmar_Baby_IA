import hmac
import os
import customtkinter as ctk
import re
from tkinter import messagebox
from datetime import datetime

import banco
from ui_components import IconEntry, PainelInstitucional, PasswordField

CODIGO_PROFISSIONAL_PADRAO = "FARMAR-PRO-2026"


class TelaCadastro:
    def __init__(self, master):
        self.master = master

        self.painel_principal = ctk.CTkFrame(
            self.master,
            fg_color="#f7f8fb",
            corner_radius=0,
        )
        self.painel_principal.pack(fill="both", expand=True)
        self.painel_principal.grid_rowconfigure(0, weight=1)
        self.painel_principal.grid_columnconfigure(0, weight=4, minsize=280)
        self.painel_principal.grid_columnconfigure(1, weight=6, minsize=430)

        self.painel_institucional = PainelInstitucional(
            self.painel_principal,
            mensagem=(
                "Comece seu acompanhamento pré-natal em um espaço "
                "feito para acolher e informar."
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

        self.rolagem_formulario = ctk.CTkScrollableFrame(
            self.painel_formulario,
            fg_color="transparent",
            corner_radius=0,
        )
        self.rolagem_formulario.grid(row=0, column=0, sticky="nsew")
        self.rolagem_formulario.grid_columnconfigure(0, weight=1)

        self.conteudo_centro = ctk.CTkFrame(
            self.rolagem_formulario,
            fg_color="transparent",
            width=380,
        )
        self.conteudo_centro.grid(row=0, column=0, padx=30, pady=34)
        self.conteudo_centro.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.conteudo_centro,
            text="Crie sua conta",
            font=("Arial", 26, "bold"),
            text_color="#243447",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))
        ctk.CTkLabel(
            self.conteudo_centro,
            text="Preencha seus dados para começar.",
            font=("Arial", 13),
            text_color="#667085",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 18))

        self.perfil_selecionado = ctk.StringVar(value="gestante")
        ctk.CTkLabel(
            self.conteudo_centro,
            text="Perfil da conta",
            font=("Arial", 12, "bold"),
            text_color="#344054",
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", pady=(0, 7))
        seletor_perfil = ctk.CTkFrame(
            self.conteudo_centro,
            fg_color="#f8fafc",
            corner_radius=10,
        )
        seletor_perfil.grid(row=3, column=0, sticky="ew", pady=(0, 2))
        seletor_perfil.grid_columnconfigure(0, weight=1)
        seletor_perfil.grid_columnconfigure(1, weight=1)
        self.botao_perfil_gestante = ctk.CTkButton(
            seletor_perfil,
            text="Gestante",
            height=38,
            fg_color="#ff6b8b",
            hover_color="#e05372",
            corner_radius=8,
            command=lambda: self.selecionar_perfil("gestante"),
        )
        self.botao_perfil_gestante.grid(
            row=0,
            column=0,
            padx=4,
            pady=4,
            sticky="ew",
        )
        self.botao_perfil_profissional = ctk.CTkButton(
            seletor_perfil,
            text="Profissional",
            height=38,
            fg_color="#e9edf2",
            text_color="#98a2b3",
            corner_radius=8,
            command=lambda: self.selecionar_perfil("profissional"),
        )
        self.botao_perfil_profissional.grid(
            row=0,
            column=1,
            padx=4,
            pady=4,
            sticky="ew",
        )
        ctk.CTkLabel(
            self.conteudo_centro,
            text="Profissionais precisam de um código de convite válido.",
            font=("Arial", 10),
            text_color="#7b8493",
            anchor="w",
        ).grid(row=4, column=0, sticky="ew", pady=(0, 13))

        self.campo_autorizacao = ctk.CTkFrame(
            self.conteudo_centro,
            fg_color="transparent",
        )
        self.campo_autorizacao.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(0, 8),
        )
        self.campo_autorizacao.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self.campo_autorizacao,
            text="Código de autorização",
            font=("Arial", 12, "bold"),
            text_color="#344054",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self.codigo_autorizacao = IconEntry(
            self.campo_autorizacao,
            icon="key",
            placeholder_text="Digite o código de convite",
            width=360,
            height=48,
        )
        self.codigo_autorizacao.grid(row=1, column=0, sticky="ew")
        self.campo_autorizacao.grid_remove()

        self.nome = self._criar_campo(
            "Nome completo",
            "user",
            "Nome e sobrenome",
            6,
        )
        self.email = self._criar_campo(
            "E-mail",
            "envelope",
            "voce@exemplo.com",
            8,
        )
        self.telefone = self._criar_campo(
            "Telefone com DDD",
            "phone",
            "(00) 00000-0000",
            10,
        )
        self.data_nasc = self._criar_campo(
            "Data de nascimento",
            "calendar",
            "DD/MM/AAAA",
            12,
        )

        self.data_nasc.bind("<KeyRelease>", self.formatar_data)

        self.senha = self._criar_campo_senha(
            "Senha (mínimo 8 caracteres)",
            14,
        )
        self.conf_senha = self._criar_campo_senha(
            "Confirmar senha",
            16,
        )

        for campo in (self.nome, self.email, self.telefone, self.data_nasc,
                      self.senha, self.conf_senha):
            campo.bind("<Return>", self._ao_pressionar_enter)

        self.termos = ctk.CTkCheckBox(
            self.conteudo_centro,
            text="Li e aceito os Termos de Uso e Política de Privacidade",
            font=("Arial", 11),
            text_color="#667085",
            fg_color="#ff6b8b",
            hover_color="#e05372",
        )
        self.termos.grid(
            row=18,
            column=0,
            sticky="w",
            pady=(12, 14),
        )

        self.botao_cadastrar = ctk.CTkButton(
            self.conteudo_centro,
            height=48,
            text="Criar conta",
            font=("Arial", 15, "bold"),
            fg_color="#c65378",
            hover_color="#a94365",
            corner_radius=12,
            command=self.executar_cadastro,
        )
        self.botao_cadastrar.grid(
            row=19,
            column=0,
            sticky="ew",
            pady=(0, 10),
        )

        self.link_login = ctk.CTkButton(
            self.conteudo_centro,
            text="Já tem uma conta?  Entrar",
            font=("Arial", 12, "bold"),
            fg_color="transparent",
            text_color="#a94365",
            hover_color="#fbeef3",
            command=self.master.abrir_login,
        )
        self.link_login.grid(row=20, column=0, pady=(0, 12))

        self.master.after(100, self.nome.focus_set)

    def selecionar_perfil(self, tipo):
        if tipo not in ("gestante", "profissional"):
            return
        self.perfil_selecionado.set(tipo)
        profissional_selecionado = tipo == "profissional"
        self.botao_perfil_profissional.configure(
            fg_color="#ff6b8b" if profissional_selecionado else "#e9edf2",
            text_color="white" if profissional_selecionado else "#667085",
        )
        self.botao_perfil_gestante.configure(
            fg_color="#e9edf2" if profissional_selecionado else "#ff6b8b",
            text_color="#667085" if profissional_selecionado else "white",
        )
        if profissional_selecionado:
            self.campo_autorizacao.grid()
        else:
            self.codigo_autorizacao.delete(0, "end")
            self.campo_autorizacao.grid_remove()

    def _criar_campo(self, rotulo, icone, placeholder, linha):
        ctk.CTkLabel(
            self.conteudo_centro,
            text=rotulo,
            font=("Arial", 12, "bold"),
            text_color="#344054",
            anchor="w",
        ).grid(row=linha, column=0, sticky="ew", pady=(0, 6))
        campo = IconEntry(
            self.conteudo_centro,
            icon=icone,
            placeholder_text=placeholder,
            width=360,
            height=48,
        )
        campo.grid(row=linha + 1, column=0, sticky="ew", pady=(0, 12))
        return campo

    def _criar_campo_senha(self, rotulo, linha):
        ctk.CTkLabel(
            self.conteudo_centro,
            text=rotulo,
            font=("Arial", 12, "bold"),
            text_color="#344054",
            anchor="w",
        ).grid(row=linha, column=0, sticky="ew", pady=(0, 6))
        campo = PasswordField(
            self.conteudo_centro,
            width=360,
            height=48,
        )
        campo.grid(row=linha + 1, column=0, sticky="ew", pady=(0, 12))
        return campo

    def formatar_data(self, event):
        """Adiciona automaticamente as barras na data enquanto digita e limita o tamanho"""
        # Ignora teclas de controle como Backspace ou Setas para não atrapalhar o usuário apagando
        if event.keysym in ("Backspace", "Delete", "Left", "Right"):
            return

        texto = self.data_nasc.get()
        # Remove qualquer caractere que não seja número
        texto_limpo = "".join([c for c in texto if c.isdigit()])

        texto_formatado = ""

        # Reconstrói a string inserindo as barras de forma automática
        if len(texto_limpo) > 0:
            texto_formatado += texto_limpo[:2]
        if len(texto_limpo) > 2:
            texto_formatado += "/" + texto_limpo[2:4]
        if len(texto_limpo) > 4:
            texto_formatado += "/" + texto_limpo[4:8] # Limita o ano em até 4 dígitos

        # Atualiza o campo com o texto formatado
        self.data_nasc.delete(0, "end")
        self.data_nasc.insert(0, texto_formatado)

    def _ao_pressionar_enter(self, event):
        self.executar_cadastro()
        return "break"

    def validar_campos(self, nome, email, telefone, data_nasc, senha, conf_senha):
        """Retorna uma mensagem de erro, ou None se estiver tudo certo"""
        if not all([nome, email, telefone, data_nasc, senha, conf_senha]):
            return "Preencha todos os campos."

        if len(nome.split()) < 2:
            return "Digite o nome completo (nome e sobrenome)."

        if re.fullmatch(r"[^@\s]+@(?:[^.@\s]+\.)+[^.@\s]+", email) is None:
            return "Digite um e-mail válido."

        digitos_telefone = "".join(c for c in telefone if c.isdigit())
        if len(digitos_telefone) not in (10, 11):
            return "Digite o telefone com DDD (10 ou 11 números)."

        try:
            nascimento = datetime.strptime(data_nasc, "%d/%m/%Y")
        except ValueError:
            return "Data de nascimento inválida. Use o formato DD/MM/AAAA."
        if nascimento > datetime.now():
            return "A data de nascimento não pode estar no futuro."

        if len(senha) < 8:
            return "A senha precisa ter pelo menos 8 caracteres."

        if senha != conf_senha:
            return "As senhas não coincidem."

        if not self.termos.get():
            return "Você precisa aceitar os Termos de Uso para continuar."

        return None

    def validar_codigo_profissional(self, codigo):
        codigo_esperado = os.environ.get(
            "FARMAR_PROFISSIONAL_CODE",
            CODIGO_PROFISSIONAL_PADRAO,
        )
        if not codigo or not hmac.compare_digest(codigo, codigo_esperado):
            return "Código de autorização profissional inválido ou não informado."
        return None

    def executar_cadastro(self):
        nome = self.nome.get().strip()
        email = self.email.get().strip()
        telefone = self.telefone.get().strip()
        data_nasc = self.data_nasc.get().strip()
        senha = self.senha.get()
        conf_senha = self.conf_senha.get()
        tipo_perfil = self.perfil_selecionado.get()

        erro = self.validar_campos(nome, email, telefone, data_nasc, senha, conf_senha)
        if erro:
            messagebox.showerror("Erro no cadastro", erro)
            return

        if tipo_perfil == "profissional":
            erro = self.validar_codigo_profissional(
                self.codigo_autorizacao.get().strip()
            )
            if erro:
                messagebox.showerror("Autorização necessária", erro)
                return

        try:
            sucesso, mensagem = banco.cadastrar_usuario(
                nome,
                email,
                telefone,
                data_nasc,
                senha,
                tipo=tipo_perfil,
            )
        except banco.ErroBanco as erro:
            messagebox.showerror("Falha no cadastro", str(erro))
            return

        if sucesso:
            messagebox.showinfo("Cadastro", mensagem + "\nAgora faça o login.")
            self.master.abrir_login()
        else:
            messagebox.showerror("Erro no cadastro", mensagem)