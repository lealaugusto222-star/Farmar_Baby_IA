import customtkinter as ctk

from cadastro import TelaCadastro
from dashboard import TelaDashboard
from dashboard_profissional import TelaDashboardProfissional
from login import TelaLogin
from main import App
from ui_components import IconEntry, PasswordField


def test_screens_and_ui_components_initialize_and_destroy(monkeypatch):
    janela = App()
    janela.geometry("1100x720")
    janela.withdraw()

    try:
        janela.limpar_janela()
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

        tela_cadastro.painel_principal.destroy()

        tela_gestante = TelaDashboard(
            janela,
            {"nome": "Ana Souza", "tipo": "gestante"},
        )
        janela.update_idletasks()
        assert tela_gestante.sidebar.winfo_exists()
        assert tela_gestante.sidebar.buttons["inicio"].cget("text") == "Início"
        assert tela_gestante.sidebar.nome_label.cget("text") == "Ana Souza"
        assert tela_gestante.sidebar.perfil_label.cget("text") == "Gestante"
        assert tela_gestante.btn_sair.winfo_exists()
        assert tela_gestante.sidebar.winfo_children()
        tela_gestante.mudar_aba("caderneta")
        janela.update_idletasks()
        tela_gestante.mudar_aba("ia")
        janela.update_idletasks()
        assert tela_gestante.caixa_chat.winfo_exists()
        tela_gestante.mudar_aba("monitoramento")
        janela.update_idletasks()
        tela_gestante.container_geral.destroy()

        monkeypatch.setattr(
            "dashboard_profissional.banco.listar_usuarios",
            lambda tipo: [],
        )
        tela_profissional = TelaDashboardProfissional(
            janela,
            {"nome": "Dra. Beatriz Lima", "tipo": "profissional"},
        )
        janela.update_idletasks()
        assert tela_profissional.sidebar.winfo_exists()
        assert tela_profissional.btn_pacientes.cget("text") == "Pacientes"
        assert (
            tela_profissional.sidebar.nome_label.cget("text")
            == "Dra. Beatriz Lima"
        )
        assert tela_profissional.sidebar.perfil_label.cget("text") == "Profissional"
        assert tela_profissional.btn_sair.winfo_exists()
        assert tela_profissional.entrada_busca.entry.winfo_exists()
        assert tela_profissional.entrada_busca.entry._entry.bind(
            "<KeyRelease>"
        )
        tela_profissional.mudar_aba("alertas")
        janela.update_idletasks()
        tela_profissional.mudar_aba("agenda")
        janela.update_idletasks()
        tela_profissional.mudar_aba("pacientes")
        janela.update_idletasks()
        tela_profissional.container_geral.destroy()
    finally:
        janela.destroy()
