import banco


def _cadastrar_gestante(email="ana@example.com", senha="senha-forte-123"):
    return banco.cadastrar_usuario(
        nome="Ana Souza",
        email=email,
        telefone="11987654321",
        data_nasc="10/05/1995",
        senha=senha,
    )


def test_login_com_credenciais_validas(monkeypatch, tmp_path):
    monkeypatch.setattr(banco, "CAMINHO_BANCO", str(tmp_path / "teste.db"))
    banco.criar_tabelas()
    assert _cadastrar_gestante()[0] is True

    usuario = banco.validar_login("ana@example.com", "senha-forte-123")

    assert usuario == {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "tipo": "gestante",
    }


def test_login_com_senha_incorreta(monkeypatch, tmp_path):
    monkeypatch.setattr(banco, "CAMINHO_BANCO", str(tmp_path / "teste.db"))
    banco.criar_tabelas()
    assert _cadastrar_gestante()[0] is True

    assert banco.validar_login("ana@example.com", "senha-errada") is None


def test_cadastro_com_email_duplicado(monkeypatch, tmp_path):
    monkeypatch.setattr(banco, "CAMINHO_BANCO", str(tmp_path / "teste.db"))
    banco.criar_tabelas()
    assert _cadastrar_gestante()[0] is True

    sucesso, mensagem = _cadastrar_gestante()

    assert sucesso is False
    assert mensagem == "Este e-mail já está cadastrado."
