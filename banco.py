import hashlib
import hmac
import os
import sqlite3
from contextlib import closing

# O banco fica na mesma pasta do projeto.
CAMINHO_BANCO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "farmar_baby.db",
)


def _conectar():
    """Abre uma conexão com o banco de dados do projeto."""
    return sqlite3.connect(CAMINHO_BANCO)


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
    with closing(_conectar()) as conexao:
        conexao.execute(
            """
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

        conexao.commit()


def cadastrar_usuario(nome, email, telefone, data_nasc, senha, tipo="gestante"):
    """Cadastra usuário. Retorna (True, mensagem) ou (False, motivo)."""
    criar_tabelas()

    if tipo not in ("gestante", "profissional"):
        return False, "Tipo de usuário inválido."

    try:
        with closing(_conectar()) as conexao:
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
            conexao.commit()

        return True, "Cadastro realizado com sucesso!"

    except sqlite3.IntegrityError:
        return False, "Este e-mail já está cadastrado."


def validar_login(email, senha, tipo="gestante"):
    """Valida e-mail, senha e perfil. Retorna os dados do usuário ou None."""
    criar_tabelas()

    with closing(_conectar()) as conexao:
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

    with closing(_conectar()) as conexao:
        linhas = conexao.execute(
            """
            SELECT id, nome, email, tipo
            FROM usuarios
            WHERE tipo = ?
            ORDER BY nome COLLATE NOCASE
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