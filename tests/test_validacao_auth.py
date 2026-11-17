import pytest

import cadastro
import login


class Campo:
    def __init__(self, valor):
        self.valor = valor

    def get(self):
        return self.valor


class Termos:
    def get(self):
        return True


class Master:
    def __init__(self):
        self.paineis_abertos = []
        self.login_aberto = False

    def abrir_dashboard(self, usuario=None):
        self.paineis_abertos.append(("gestante", usuario))

    def abrir_dashboard_profissional(self):
        self.paineis_abertos.append(("profissional", None))

    def abrir_login(self):
        self.login_aberto = True


def _tela_login(email, senha):
    tela = login.TelaLogin.__new__(login.TelaLogin)
    tela.usuario = Campo(email)
    tela.senha = Campo(senha)
    tela.perfil_selecionado = Campo("Gestante")
    tela.master = Master()
    return tela


@pytest.mark.parametrize(
    ("email", "senha"),
    [
        ("", ""),
        ("ana@.com", "senha-forte-123"),
    ],
)
def test_login_recusa_campos_vazios_ou_email_invalido(
    monkeypatch, email, senha
):
    tela = _tela_login(email, senha)
    erros = []
    chamadas_banco = []
    monkeypatch.setattr(
        login.messagebox,
        "showerror",
        lambda *args: erros.append(args),
    )
    monkeypatch.setattr(
        login.banco,
        "validar_login",
        lambda *args: chamadas_banco.append(args),
    )

    tela.validar_login()

    assert erros
    assert chamadas_banco == []
    assert tela.master.paineis_abertos == []


def test_login_com_email_valido_consulta_banco(monkeypatch):
    tela = _tela_login("ana@example.com", "senha-forte-123")
    usuario = {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "tipo": "gestante",
    }
    monkeypatch.setattr(login.banco, "validar_login", lambda *args: usuario)

    tela.validar_login()

    assert tela.master.paineis_abertos == [("gestante", usuario)]


def _tela_cadastro():
    tela = cadastro.TelaCadastro.__new__(cadastro.TelaCadastro)
    tela.termos = Termos()
    return tela


def _dados_cadastro(**alteracoes):
    dados = {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "telefone": "11987654321",
        "data_nasc": "10/05/1995",
        "senha": "senha123",
        "conf_senha": "senha123",
    }
    dados.update(alteracoes)
    return dados


def test_cadastro_recusa_campos_vazios():
    erro = _tela_cadastro().validar_campos(
        **_dados_cadastro(email="")
    )

    assert erro == "Preencha todos os campos."


@pytest.mark.parametrize("email", ["ana-invalido", "ana@.com"])
def test_cadastro_recusa_email_invalido(email):
    erro = _tela_cadastro().validar_campos(
        **_dados_cadastro(email=email)
    )

    assert erro == "Digite um e-mail válido."


def test_cadastro_exige_senha_minima_de_oito_caracteres():
    erro = _tela_cadastro().validar_campos(
        **_dados_cadastro(senha="senha12", conf_senha="senha12")
    )

    assert erro == "A senha precisa ter pelo menos 8 caracteres."


def test_cadastro_aceita_senha_minima_de_oito_caracteres():
    erro = _tela_cadastro().validar_campos(
        **_dados_cadastro(senha="senha123", conf_senha="senha123")
    )

    assert erro is None


@pytest.mark.parametrize(
    ("codigo", "esperado", "erro"),
    [
        ("codigo-valido", "codigo-valido", None),
        ("codigo-invalido", "codigo-valido", True),
        ("", "codigo-valido", True),
    ],
)
def test_validacao_codigo_profissional(monkeypatch, codigo, esperado, erro):
    monkeypatch.setenv("FARMAR_PROFISSIONAL_CODE", esperado)
    resultado = _tela_cadastro().validar_codigo_profissional(codigo)

    if erro:
        assert resultado == (
            "Código de autorização profissional inválido ou não informado."
        )
    else:
        assert resultado is None


def test_codigo_profissional_padrao_quando_variavel_ausente(monkeypatch):
    monkeypatch.delenv("FARMAR_PROFISSIONAL_CODE", raising=False)

    assert _tela_cadastro().validar_codigo_profissional(
        cadastro.CODIGO_PROFISSIONAL_PADRAO
    ) is None


def test_cadastro_profissional_valida_codigo_e_envia_tipo_ao_banco(monkeypatch):
    tela = _tela_cadastro()
    tela.nome = Campo("Ana Souza")
    tela.email = Campo("ana@example.com")
    tela.telefone = Campo("11987654321")
    tela.data_nasc = Campo("10/05/1995")
    tela.senha = Campo("senha123")
    tela.conf_senha = Campo("senha123")
    tela.perfil_selecionado = Campo("profissional")
    tela.codigo_autorizacao = Campo("codigo-valido")
    tela.master = Master()
    chamadas_banco = []
    monkeypatch.setenv("FARMAR_PROFISSIONAL_CODE", "codigo-valido")
    monkeypatch.setattr(
        cadastro.banco,
        "cadastrar_usuario",
        lambda *args, **kwargs: (
            chamadas_banco.append((args, kwargs))
            or (True, "Cadastro realizado com sucesso!")
        ),
    )
    monkeypatch.setattr(cadastro.messagebox, "showinfo", lambda *args: None)

    tela.executar_cadastro()

    assert len(chamadas_banco) == 1
    assert chamadas_banco[0][1]["tipo"] == "profissional"
    assert tela.master.login_aberto


@pytest.mark.parametrize("codigo", ["codigo-errado", ""])
def test_codigo_profissional_incorreto_bloqueia_cadastro(
    monkeypatch, codigo
):
    tela = _tela_cadastro()
    tela.nome = Campo("Ana Souza")
    tela.email = Campo("ana@example.com")
    tela.telefone = Campo("11987654321")
    tela.data_nasc = Campo("10/05/1995")
    tela.senha = Campo("senha123")
    tela.conf_senha = Campo("senha123")
    tela.perfil_selecionado = Campo("profissional")
    tela.codigo_autorizacao = Campo(codigo)
    erros = []
    chamadas_banco = []
    monkeypatch.setenv("FARMAR_PROFISSIONAL_CODE", "codigo-valido")
    monkeypatch.setattr(
        cadastro.messagebox,
        "showerror",
        lambda *args: erros.append(args),
    )
    monkeypatch.setattr(
        cadastro.banco,
        "cadastrar_usuario",
        lambda *args, **kwargs: chamadas_banco.append((args, kwargs)),
    )

    tela.executar_cadastro()

    assert erros
    assert "autorização" in erros[0][1].lower()
    assert chamadas_banco == []
