from base_model import BaseModel

class FuncionarioModel(BaseModel):
    """Gerencia a persistência da entidade Funcionários."""

    def listar_todos(self) -> list[dict]:
        # crie a estrutura de select para listar todos os funcionários com os campos id, nome, cpf, cargo, telefone, salario e ativo
        query = """
            SELECT id, nome, cpf, cargo, telefone, salario, ativo
            FROM funcionarios
            ORDER BY nome ASC
        """
        return self.fetch_all(query)

    def listar_ativos(self) -> list[dict]:
        # crie a estrutura de select para listar os funcionários ativos com os campos id, nome e cargo
        query = """
            SELECT id, nome, cargo
            FROM funcionarios
            WHERE ativo = TRUE
            ORDER BY nome ASC
        """
        return self.fetch_all(query)

    def buscar_por_id(self, func_id: int) -> dict | None:
        # crie a estrutura de select para buscar um funcionário pelo ID com os campos id, nome, cpf, cargo, telefone, salario e ativo
        query = """
            SELECT id, nome, cpf, cargo, telefone, salario, ativo
            FROM funcionarios
            WHERE id = %s
        """
        return self.fetch_one(query, (func_id,))

    def criar(self, nome: str, cpf: str, cargo: str, telefone: str, salario: float) -> int:
        # crie a estrutura de insert para adicionar um novo funcionário com os campos nome, cpf, cargo, telefone, salario e ativo
        query = """
            INSERT INTO funcionarios (nome, cpf, cargo, telefone, salario, ativo)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """
        return self.execute_query(query, (nome, cpf, cargo, telefone, salario))

    def atualizar(
        self,
        func_id: int,
        nome: str,
        cpf: str,
        cargo: str,
        telefone: str,
        salario: float,
        ativo: bool,
    ) -> None:
        # crie a estrutura de update para atualizar um funcionário existente com os campos nome, cpf, cargo, telefone, salario e ativo
        query = """
            UPDATE funcionarios
            SET nome = %s, cpf = %s, cargo = %s, telefone = %s, salario = %s, ativo = %s
            WHERE id = %s
        """
        self.execute_query(query, (nome, cpf, cargo, telefone, salario, ativo, func_id))

    def excluir(self, func_id: int) -> None:
        # crie a estrutura de delete para excluir um funcionário pelo ID
        query = "DELETE FROM funcionarios WHERE id = %s"
        self.execute_query(query, (func_id,))