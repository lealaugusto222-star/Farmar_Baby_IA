import os
import mysql.connector
import mysql.connector.connection as MySQLConnection
import dotenv

dotenv.load_dotenv()
class DatabaseConnection:
    """Fábrica centralizada para gerenciamento de conexões com o MySQL."""

    @staticmethod
    def get_connection() -> MySQLConnection:
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            return connection
        except mysql.connector.Error as err:
            raise ConnectionError(f"Erro ao conectar ao banco de dados MySQL: {err}")

    @staticmethod
    def testar_conexao() -> bool:
        """Valida se as credenciais do .env estabelecem conexão ativa."""
        conn = None
        try:
            conn = DatabaseConnection.get_connection()
            return conn.is_connected()
        finally:
            if conn and conn.is_connected():
                conn.close()