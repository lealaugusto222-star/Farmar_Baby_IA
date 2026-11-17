import sqlite3

import banco
import login


def _usar_banco_temporario(monkeypatch, tmp_path):
    caminho = str(tmp_path / "teste.db")
    monkeypatch.setattr(banco, "CAMINHO_BANCO", caminho)
    banco.criar_tabelas()
    return caminho


def _cadastrar_gestante(email="ana@example.com", senha="senha-forte-123"):
    return banco.cadastrar_usuario(
        nome="Ana Souza",
        email=email,
        telefone="11987654321",
        data_nasc="10/05/1995",
        senha=senha,
    )


def test_login_com_credenciais_validas(monkeypatch, tmp_path):
    _usar_banco_temporario(monkeypatch, tmp_path)
    assert _cadastrar_gestante()[0] is True

    usuario = banco.validar_login("ana@example.com", "senha-forte-123")

    assert usuario == {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "tipo": "gestante",
    }


def test_login_com_senha_incorreta(monkeypatch, tmp_path):
    _usar_banco_temporario(monkeypatch, tmp_path)
    assert _cadastrar_gestante()[0] is True

    assert banco.validar_login("ana@example.com", "senha-errada") is None


def test_cadastro_com_email_duplicado(monkeypatch, tmp_path):
    _usar_banco_temporario(monkeypatch, tmp_path)
    assert _cadastrar_gestante()[0] is True

    sucesso, mensagem = _cadastrar_gestante()

    assert sucesso is False
    assert mensagem == "Este e-mail já está cadastrado."


def test_nao_cria_conta_profissional_com_senha_padrao(monkeypatch, tmp_path):
    _usar_banco_temporario(monkeypatch, tmp_path)

    assert banco.validar_login(
        "profissional@farmarbaby.com",
        "123456",
        "profissional",
    ) is None


def test_remove_conta_profissional_legada_com_senha_padrao(monkeypatch, tmp_path):
    caminho = _usar_banco_temporario(monkeypatch, tmp_path)
    with sqlite3.connect(caminho) as conexao:
        conexao.execute(
            """
            INSERT INTO usuarios
                (nome, email, telefone, data_nasc, senha_hash, tipo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Profissional Teste",
                "profissional@farmarbaby.com",
                "00000000000",
                "01/01/1980",
                banco._gerar_hash("123456"),
                "profissional",
            ),
        )

    assert banco.validar_login(
        "profissional@farmarbaby.com",
        "123456",
        "profissional",
    ) is None

    with sqlite3.connect(caminho) as conexao:
        conta = conexao.execute(
            "SELECT 1 FROM usuarios WHERE email = ?",
            ("profissional@farmarbaby.com",),
        ).fetchone()

    assert conta is None


def test_preserva_conta_profissional_com_senha_alterada(monkeypatch, tmp_path):
    _usar_banco_temporario(monkeypatch, tmp_path)
    assert banco.cadastrar_usuario(
        nome="Profissional",
        email="profissional@farmarbaby.com",
        telefone="11987654321",
        data_nasc="10/05/1980",
        senha="senha-nova-e-segura",
        tipo="profissional",
    )[0] is True

    banco.criar_tabelas()

    assert banco.validar_login(
        "profissional@farmarbaby.com",
        "senha-nova-e-segura",
        "profissional",
    ) is not None


def test_credencial_de_teste_nao_abre_painel(monkeypatch):
    class Campo:
        def __init__(self, valor):
            self.valor = valor

        def get(self):
            return self.valor

    class Master:
        def __init__(self):
            self.paineis_abertos = []

        def abrir_dashboard(self, usuario=None):
            self.paineis_abertos.append(("gestante", usuario))

        def abrir_dashboard_profissional(self, usuario=None):
            self.paineis_abertos.append(("profissional", usuario))

    tela = login.TelaLogin.__new__(login.TelaLogin)
    tela.usuario = Campo("admin@example.com")
    tela.senha = Campo("1234")
    tela.perfil_selecionado = Campo("Profissional")
    tela.master = Master()
    erros = []
    monkeypatch.setattr(login.messagebox, "showerror", lambda *args: erros.append(args))
    monkeypatch.setattr(login.banco, "validar_login", lambda *args: None)

    tela.validar_login()

    assert tela.master.paineis_abertos == []
    assert erros
