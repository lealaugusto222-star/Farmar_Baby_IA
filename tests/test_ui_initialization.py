import customtkinter as ctk

from login import TelaLogin
from ui_components import IconEntry, PasswordField


def test_login_and_ui_components_initialize_and_destroy():
    janela = ctk.CTk()
    janela.geometry("1100x720")
    janela.withdraw()
    janela.abrir_cadastro = lambda: None

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
        janela.after(120, janela.quit)
        janela.mainloop()

        assert tela_login.usuario.entry.winfo_exists()
        assert tela_login.senha.entry.winfo_exists()
        assert campo_email.entry.winfo_exists()
        assert campo_senha.entry.winfo_exists()
    finally:
        janela.destroy()
