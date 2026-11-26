from config_database import DatabaseConnection


class BaseModel:
    """Classe base para operações CRUD com gerenciamento seguro de conexão e cursor."""

    def fetch_all(self, query: str, params: tuple | None = None) -> list[dict]:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query: str, params: tuple | None = None) -> dict | None:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def execute_query(self, query: str, params: tuple | None = None) -> int:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except Exception as err:
            conn.rollback()
            raise err
        finally:
            cursor.close()
            conn.close()