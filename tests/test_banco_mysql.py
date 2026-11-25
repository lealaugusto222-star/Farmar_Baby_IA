import sqlite3

import pytest

import banco


class CursorSimulado:
    def __init__(self):
        self.consultas = []
        self.resultado = None

    def execute(self, consulta, parametros=()):
        self.consultas.append((consulta, parametros))
        if consulta.startswith("SELECT senha_hash"):
            self.resultado = None
        return self

    def fetchone(self):
        return self.resultado


class ConexaoSimulada:
    def __init__(self):
        self.cursor_simulado = CursorSimulado()
        self.commits = 0
        self.rollbacks = 0
        self.fechada = False

    def cursor(self):
        return self.cursor_simulado

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.fechada = True


def _configurar_mysql(monkeypatch, conexao):
    configuracao = {}
    monkeypatch.setenv("DB_TYPE", "mysql")
    monkeypatch.setenv("DB_HOST", "db.example.test")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_USER", "farmar_app")
    monkeypatch.setenv("DB_PASSWORD", "senha-de-teste")
    monkeypatch.setenv("DB_NAME", "farmar_baby")

    def conectar(**kwargs):
        configuracao.update(kwargs)
        return conexao

    monkeypatch.setattr(banco.mysql.connector, "connect", conectar)
    return configuracao


def test_mysql_configura_conexao_ddl_placeholders_e_transacao(monkeypatch):
    conexao = ConexaoSimulada()
    configuracao = _configurar_mysql(monkeypatch, conexao)

    banco.criar_tabelas()

    assert configuracao == {
        "host": "db.example.test",
        "port": 3307,
        "user": "farmar_app",
        "password": "senha-de-teste",
        "database": "farmar_baby",
        "charset": "utf8mb4",
        "ssl_disabled": False,
    }
    consultas = conexao.cursor_simulado.consultas
    assert "AUTO_INCREMENT" in consultas[0][0]
    assert "CREATE TABLE IF NOT EXISTS usuarios" in consultas[0][0]
    assert all(
        coluna in consultas[0][0]
        for coluna in (
            "id_usuario ",
            "nome_completo ",
            "email ",
            "telefone ",
            "data_nascimento ",
            "senha_hash ",
            "tipo ",
        )
    )
    assert "?" not in consultas[1][0]
    assert "%s" in consultas[1][0]
    assert consultas[1][1] == (
        "profissional@farmarbaby.com",
        "profissional",
    )
    assert conexao.commits == 1
    assert conexao.fechada


def test_mysql_cadastro_usa_placeholders_e_hash_sem_senha_pura(monkeypatch):
    conexao = ConexaoSimulada()
    _configurar_mysql(monkeypatch, conexao)

    sucesso, mensagem = banco.cadastrar_usuario(
        "Ana Souza",
        "ANA@example.com",
        "11987654321",
        "10/05/1995",
        "senha-forte-123",
    )

    assert sucesso is True
    assert mensagem == "Cadastro realizado com sucesso!"
    consultas = conexao.cursor_simulado.consultas
    insercao = next(
        (consulta, parametros)
        for consulta, parametros in consultas
        if consulta.strip().startswith("INSERT INTO usuarios")
    )
    assert "%s" in insercao[0]
    assert "?" not in insercao[0]
    assert insercao[1][:4] == (
        "Ana Souza",
        "ana@example.com",
        "11987654321",
        "1995-05-10",
    )
    assert "nome_completo" in insercao[0]
    assert "data_nascimento" in insercao[0]
    assert insercao[1][4] != "senha-forte-123"
    assert insercao[1][5] == "gestante"


@pytest.mark.parametrize("db_type", [None, "sqlite"])
def test_db_type_padrao_e_sqlite_fallback(monkeypatch, tmp_path, db_type):
    if db_type is None:
        monkeypatch.delenv("DB_TYPE", raising=False)
    else:
        monkeypatch.setenv("DB_TYPE", db_type)
    caminho = str(tmp_path / "fallback.db")
    monkeypatch.setattr(banco, "CAMINHO_BANCO", caminho)

    banco.criar_tabelas()

    with sqlite3.connect(caminho) as conexao:
        colunas = [
            linha[1]
            for linha in conexao.execute("PRAGMA table_info(usuarios)")
        ]
    assert colunas == [
        "id_usuario",
        "nome_completo",
        "email",
        "telefone",
        "data_nascimento",
        "senha_hash",
        "tipo",
    ]


def test_mysql_sem_configuracao_essencial_nao_cai_silenciosamente_em_sqlite(
    monkeypatch,
):
    monkeypatch.setenv("DB_TYPE", "mysql")
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

    with pytest.raises(banco.ErroBanco, match="DB_HOST, DB_USER e DB_NAME"):
        banco.criar_tabelas()


def test_db_type_invalido_e_rejeitado(monkeypatch):
    monkeypatch.setenv("DB_TYPE", "postgres")

    with pytest.raises(banco.ErroBanco, match="DB_TYPE"):
        banco.criar_tabelas()
