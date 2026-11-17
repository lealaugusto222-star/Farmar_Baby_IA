import customtkinter as ctk

from cadastro import TelaCadastro
from login import TelaLogin
from ui_components import IconEntry, PasswordField


def test_login_signup_and_ui_components_initialize_and_destroy():
    janela = ctk.CTk()
    janela.geometry("1100x720")
    janela.withdraw()
    janela.abrir_cadastro = lambda: None
    janela.abrir_login = lambda: None

    try:
        tela_login = TelaLogin(janela)
        componentes = ctk.CTkFrame(janela)
        campo_email = IconEntry(
            componentes,
            icon="envelope",
            placeholder_text="E-mail",
        )
        campo_senha = PasswordField(componentes)
        campo_email.pack()
        campo_senha.pack()

        binding_original = campo_email.entry._entry.bind("<FocusIn>")
        campo_email.bind("<FocusIn>", lambda event: None)
        binding_complementado = campo_email.entry._entry.bind("<FocusIn>")
        assert binding_original in binding_complementado

        binding_original_senha = campo_senha.entry._entry.bind("<FocusIn>")
        campo_senha.bind("<FocusIn>", lambda event: None)
        binding_complementado_senha = campo_senha.entry._entry.bind("<FocusIn>")
        assert binding_original_senha in binding_complementado_senha

        janela.update_idletasks()
        assert tela_login.usuario.entry.winfo_exists()
        assert tela_login.senha.entry.winfo_exists()
        assert campo_email.entry.winfo_exists()
        assert campo_senha.entry.winfo_exists()

        janela.after_cancel(tela_login._focus_after_id)
        tela_login.painel_principal.destroy()
        componentes.destroy()

        tela_cadastro = TelaCadastro(janela)
        janela.update_idletasks()
        janela.after(120, janela.quit)
        janela.mainloop()

        assert tela_cadastro.nome.entry.winfo_exists()
        assert tela_cadastro.email.entry.winfo_exists()
        assert tela_cadastro.telefone.entry.winfo_exists()
        assert tela_cadastro.data_nasc.entry.winfo_exists()
        assert tela_cadastro.senha.entry.winfo_exists()
        assert tela_cadastro.conf_senha.entry.winfo_exists()
        assert tela_cadastro.perfil_selecionado.get() == "gestante"
        assert str(tela_cadastro.botao_perfil_profissional.cget("state")) == "normal"
        assert not tela_cadastro.campo_autorizacao.grid_info()

        tela_cadastro.selecionar_perfil("profissional")
        janela.update_idletasks()
        assert tela_cadastro.perfil_selecionado.get() == "profissional"
        assert tela_cadastro.codigo_autorizacao.entry.winfo_exists()
        assert tela_cadastro.campo_autorizacao.grid_info()

        tela_cadastro.selecionar_perfil("profissional")
        assert tela_cadastro.perfil_selecionado.get() == "profissional"
        tela_cadastro.selecionar_perfil("gestante")
        assert tela_cadastro.perfil_selecionado.get() == "gestante"
        assert not tela_cadastro.campo_autorizacao.grid_info()
        for campo in (
            tela_cadastro.nome,
            tela_cadastro.email,
            tela_cadastro.telefone,
            tela_cadastro.data_nasc,
            tela_cadastro.senha,
            tela_cadastro.conf_senha,
        ):
            assert campo.entry._entry.bind("<Return>")

        binding_original = tela_cadastro.data_nasc.entry._entry.bind(
            "<KeyRelease>"
        )
        tela_cadastro.data_nasc.bind("<KeyRelease>", lambda event: None)
        binding_complementado = tela_cadastro.data_nasc.entry._entry.bind(
            "<KeyRelease>"
        )
        assert binding_original in binding_complementado
    finally:
        janela.destroy()
