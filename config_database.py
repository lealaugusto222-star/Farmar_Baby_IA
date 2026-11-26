import os

import mysql.connector
from dotenv import load_dotenv


class DatabaseConnectionError(Exception):
    """Indica configuração ou conexão de banco inválida."""


class MySQLConnectionAdapter:
    """Adapta o cursor MySQL à API compatível utilizada pelo projeto."""

    def __init__(self, connection):
        self._connection = connection

    @property
    def database_type(self):
        return "mysql"

    def cursor(self, dictionary=False):
        try:
            return self._connection.cursor(dictionary=dictionary)
        except TypeError:
            return self._connection.cursor()

    def execute(self, consulta, parametros=()):
        cursor = self.cursor()
        cursor.execute(
            consulta.replace("?", "%s"),
            parametros,
        )
        return cursor

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()

    def is_connected(self):
        is_connected = getattr(self._connection, "is_connected", None)
        return is_connected() if callable(is_connected) else True


class DatabaseConnection:
    """Fábrica única de conexões MySQL."""

    @staticmethod
    def load_environment(base_directory=None):
        """Carrega o .env da raiz informada sem sobrescrever variáveis existentes."""
        raiz = base_directory or os.path.dirname(os.path.abspath(__file__))
        load_dotenv(
            dotenv_path=os.path.join(raiz, ".env"),
        )

    @staticmethod
    def get_connection():
        host = os.environ.get("DB_HOST", "").strip()
        usuario = os.environ.get("DB_USER", "").strip()
        nome = os.environ.get("DB_NAME", "").strip()
        if not host or not usuario or not nome:
            raise DatabaseConnectionError(
                "Para usar MySQL, configure DB_HOST, DB_USER e DB_NAME."
            )

        try:
            porta = int(os.environ.get("DB_PORT", "3306"))
        except (TypeError, ValueError) as erro:
            raise DatabaseConnectionError(
                "DB_PORT deve ser um número inteiro."
            ) from erro
        if not 1 <= porta <= 65535:
            raise DatabaseConnectionError(
                "DB_PORT deve estar entre 1 e 65535."
            )

        try:
            connection = mysql.connector.connect(
                host=host,
                port=porta,
                user=usuario,
                password=os.environ.get("DB_PASSWORD", ""),
                database=nome,
                charset="utf8mb4",
                ssl_disabled=False,
            )
            return MySQLConnectionAdapter(connection)
        except mysql.connector.Error as erro:
            raise DatabaseConnectionError(
                f"Erro ao conectar ao banco de dados MySQL: {erro}"
            ) from erro

    @staticmethod
    def testar_conexao():
        """Valida se as configurações estabelecem uma conexão ativa."""
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            return connection.is_connected()
        finally:
            if connection is not None:
                connection.close()


DatabaseConnection.load_environment()