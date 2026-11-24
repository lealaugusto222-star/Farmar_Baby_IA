import hashlib
import hmac
import logging
import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv
import mysql.connector

load_dotenv(
    dotenv_path=os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".env",
    )
)

# O banco fica na mesma pasta do projeto.
CAMINHO_BANCO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "farmar_baby.db",
)

logger = logging.getLogger(__name__)

_DDL_SQLITE = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        telefone TEXT NOT NULL,
        data_nasc TEXT NOT NULL,
        senha_hash TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'gestante'
    )
"""

_DDL_MYSQL = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome TEXT NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        telefone TEXT NOT NULL,
        data_nasc TEXT NOT NULL,
        senha_hash VARCHAR(255) NOT NULL,
        tipo VARCHAR(32) NOT NULL DEFAULT 'gestante'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


class ErroBanco(Exception):
    """Indica uma falha de acesso ou operação no banco de dados."""


class _ConexaoMySQL:
    """Adapta a API de execução MySQL ao uso de execute do SQLite."""

    def __init__(self, conexao):
        self._conexao = conexao

    def execute(self, consulta, parametros=()):
        cursor = self._conexao.cursor()
        cursor.execute(consulta.replace("?", "%s"), parametros)
        return cursor

    def commit(self):
        self._conexao.commit()

    def rollback(self):
        self._conexao.rollback()

    def close(self):
        self._conexao.close()


def _tipo_banco():
    tipo = os.environ.get("DB_TYPE", "sqlite").strip().lower()
    if tipo not in ("sqlite", "mysql"):
        raise ErroBanco("DB_TYPE deve ser 'sqlite' ou 'mysql'.")
    return tipo


def _conectar_mysql():
    host = os.environ.get("DB_HOST", "").strip()
    usuario = os.environ.get("DB_USER", "").strip()
    nome = os.environ.get("DB_NAME", "").strip()
    if not host or not usuario or not nome:
        raise ErroBanco(
            "Para usar MySQL, configure DB_HOST, DB_USER e DB_NAME."
        )

    try:
        porta = int(os.environ.get("DB_PORT", "3306"))
    except ValueError as erro:
        raise ErroBanco("DB_PORT deve ser um número inteiro.") from erro
    if not 1 <= porta <= 65535:
        raise ErroBanco("DB_PORT deve estar entre 1 e 65535.")

    conexao = mysql.connector.connect(
        host=host,
        port=porta,
        user=usuario,
        password=os.environ.get("DB_PASSWORD", ""),
        database=nome,
        charset="utf8mb4",
        ssl_disabled=False,
    )
    return _ConexaoMySQL(conexao)


@contextmanager
def _conectar():
    """Fornece uma conexão transacional e garante rollback e fechamento."""
    tipo = _tipo_banco()
    conexao = None
    try:
        if tipo == "mysql":
            conexao = _conectar_mysql()
        else:
            conexao = sqlite3.connect(CAMINHO_BANCO)
        yield conexao
        conexao.commit()
    except (sqlite3.Error, mysql.connector.Error) as erro:
        if conexao is not None:
            conexao.rollback()
        logger.exception("Falha ao acessar o banco de dados.")
        raise ErroBanco(
            "Não foi possível acessar os dados. Tente novamente."
        ) from erro
    finally:
        if conexao is not None:
            conexao.close()


def _gerar_hash(senha, salt=None):
    """Gera um hash seguro da senha, sem armazenar a senha pura."""
    if salt is None:
        salt = os.urandom(16)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        100_000,
    )
    return salt.hex() + ":" + resultado.hex()


def _conferir_hash(senha, hash_guardado):
    """Compara uma senha digitada com o hash armazenado."""
    try:
        salt_hex, _ = hash_guardado.split(":", 1)
        novo = _gerar_hash(senha, bytes.fromhex(salt_hex))
        return hmac.compare_digest(novo, hash_guardado)
    except (ValueError, TypeError):
        return False


def criar_tabelas():
    """Cria a tabela e remove a conta profissional com a senha de demonstração."""
    with _conectar() as conexao:
        conexao.execute(
            _DDL_MYSQL if _tipo_banco() == "mysql" else _DDL_SQLITE
        )

        conta_padrao = conexao.execute(
            """
            SELECT senha_hash
            FROM usuarios
            WHERE email = ? AND tipo = ?
            """,
            ("profissional@farmarbaby.com", "profissional"),
        ).fetchone()

        if conta_padrao and _conferir_hash("123456", conta_padrao[0]):
            conexao.execute(
                "DELETE FROM usuarios WHERE email = ? AND tipo = ?",
                ("profissional@farmarbaby.com", "profissional"),
            )


def cadastrar_usuario(nome, email, telefone, data_nasc, senha, tipo="gestante"):
    """Cadastra usuário. Retorna (True, mensagem) ou (False, motivo)."""
    if tipo not in ("gestante", "profissional"):
        return False, "Tipo de usuário inválido."

    try:
        criar_tabelas()
        with _conectar() as conexao:
            try:
                conexao.execute(
                    """
                    INSERT INTO usuarios
                        (nome, email, telefone, data_nasc, senha_hash, tipo)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        nome.strip(),
                        email.strip().lower(),
                        telefone.strip(),
                        data_nasc.strip(),
                        _gerar_hash(senha),
                        tipo,
                    ),
                )
            except (sqlite3.IntegrityError, mysql.connector.IntegrityError):
                return False, "Este e-mail já está cadastrado."

        return True, "Cadastro realizado com sucesso!"

    except ErroBanco as erro:
        return False, str(erro)


def validar_login(email, senha, tipo="gestante"):
    """Valida e-mail, senha e perfil. Retorna os dados do usuário ou None."""
    criar_tabelas()

    with _conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT nome, email, tipo, senha_hash
            FROM usuarios
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()

    if linha is None:
        return None

    nome, email_banco, tipo_banco, senha_hash = linha

    if tipo_banco != tipo or not _conferir_hash(senha, senha_hash):
        return None

    return {
        "nome": nome,
        "email": email_banco,
        "tipo": tipo_banco,
    }


def listar_usuarios(tipo="gestante"):
    """
    Lista usuários de um perfil para preencher as telas do sistema.

    Retorna somente id, nome, e-mail e tipo; não retorna telefone, data de
    nascimento nem hash da senha, pois essas informações não são necessárias
    para a lista de pacientes do painel profissional.
    """
    if tipo not in ("gestante", "profissional"):
        return []

    criar_tabelas()

    with _conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT id, nome, email, tipo
            FROM usuarios
            WHERE tipo = ?
            ORDER BY LOWER(nome)
            """,
            (tipo,),
        ).fetchall()

    return [
        {
            "id": linha[0],
            "nome": linha[1],
            "email": linha[2],
            "tipo": linha[3],
        }
        for linha in linhas
    ]


def obter_usuario(email):
    """Retorna dados cadastrais de um usuário, sem expor o hash da senha."""
    criar_tabelas()

    with _conectar() as conexao:
        linha = conexao.execute(
            """
            SELECT id, nome, email, telefone, data_nasc, tipo
            FROM usuarios
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()

    if linha is None:
        return None

    return {
        "id": linha[0],
        "nome": linha[1],
        "email": linha[2],
        "telefone": linha[3],
        "data_nasc": linha[4],
        "tipo": linha[5],
    }