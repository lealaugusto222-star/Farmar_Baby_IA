import pytest

import banco
import config_database


class CursorSimulado:
    def __init__(self):
        self.consultas = []
        self.resultado = None

    def execute(self, consulta, parametros=()):
        self.consultas.append((consulta, parametros))
        return self

    def fetchone(self):
        return self.resultado

    def fetchall(self):
        return []

    def close(self):
        pass


class ConexaoSimulada:
    def __init__(self):
        self.cursor_simulado = CursorSimulado()
        self.commits = 0
        self.rollbacks = 0
        self.fechada = False

    def cursor(self, dictionary=False):
        del dictionary
        return self.cursor_simulado

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.fechada = True

    def is_connected(self):
        return True


def _configurar_mysql(monkeypatch, conexao):
    configuracao = {}
    monkeypatch.setenv("DB_HOST", "db.example.test")
    monkeypatch.setenv("DB_PORT", "3307")
    monkeypatch.setenv("DB_USER", "farmar_app")
    monkeypatch.setenv("DB_PASSWORD", "senha-de-teste")
    monkeypatch.setenv("DB_NAME", "farmar_baby")

    def conectar(**kwargs):
        configuracao.update(kwargs)
        return conexao

    monkeypatch.setattr(config_database.mysql.connector, "connect", conectar)
    return configuracao


def test_mysql_configura_ssl_ddl_placeholders_e_transacao(monkeypatch):
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
    assert "senha_hast VARCHAR(255) NOT NULL" in consultas[0][0]
    assert len(consultas) == 1
    assert all(
        "DELETE FROM usuarios" not in consulta
        for consulta, _ in consultas
    )
    assert conexao.commits == 1
    assert conexao.fechada


def test_mysql_cadastro_usa_placeholders_e_hash(monkeypatch):
    conexao = ConexaoSimulada()
    _configurar_mysql(monkeypatch, conexao)

    sucesso, mensagem = banco.cadastrar_usuario(
        "Ana Souza",
        "ANA@example.com",
        "11987654321",
        "10/05/1995",
        "senha-forte-123",
    )

    assert sucesso
    assert mensagem == "Cadastro realizado com sucesso!"
    consultas = conexao.cursor_simulado.consultas
    insercao = next(
        item
        for item in consultas
        if item[0].strip().startswith("INSERT INTO usuarios")
    )
    assert "senha_hast" in insercao[0]
    assert "senha_hash" not in insercao[0]
    assert "%s" in insercao[0]
    assert "?" not in insercao[0]
    assert insercao[1][:4] == (
        "Ana Souza",
        "ana@example.com",
        "11987654321",
        "1995-05-10",
    )
    assert banco._conferir_hash("senha-forte-123", insercao[1][4])
    assert not banco._conferir_hash("senha-incorreta", insercao[1][4])
    assert insercao[1][5] == "gestante"


def test_mysql_login_usa_senha_hast_e_migra_hash_legado(monkeypatch):
    conexao = ConexaoSimulada()
    _configurar_mysql(monkeypatch, conexao)
    conexao.cursor_simulado.resultado = (
        "Ana Souza",
        "ana@example.com",
        "gestante",
        "senha-legada",
    )

    usuario = banco.validar_login(
        "ana@example.com",
        "senha-legada",
    )

    assert usuario == {
        "nome": "Ana Souza",
        "email": "ana@example.com",
        "tipo": "gestante",
    }
    consultas = conexao.cursor_simulado.consultas
    leitura = next(
        consulta
        for consulta, _ in consultas
        if "SELECT nome_completo, email, tipo" in consulta
    )
    atualizacao, parametros_atualizacao = next(
        item
        for item in consultas
        if item[0].strip().startswith("UPDATE usuarios")
    )
    assert "senha_hast" in leitura
    assert "senha_hash" not in leitura
    assert "SET senha_hast = %s" in atualizacao
    assert "WHERE email = %s AND senha_hast = %s" in atualizacao
    assert banco._conferir_hash(
        "senha-legada",
        parametros_atualizacao[0],
    )
    assert parametros_atualizacao[1:] == (
        "ana@example.com",
        "senha-legada",
    )


def test_mysql_sem_configuracao_essencial_rejeita_conexao(monkeypatch):
    monkeypatch.delenv("DB_HOST", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)

    with pytest.raises(banco.ErroBanco, match="DB_HOST, DB_USER e DB_NAME"):
        banco.criar_tabelas()


def test_mysql_porta_invalida_rejeitada(monkeypatch):
    monkeypatch.setenv("DB_HOST", "db.example.test")
    monkeypatch.setenv("DB_USER", "farmar_app")
    monkeypatch.setenv("DB_NAME", "farmar_baby")
    monkeypatch.setenv("DB_PORT", "porta")

    with pytest.raises(banco.ErroBanco, match="DB_PORT"):
        banco.criar_tabelas()
