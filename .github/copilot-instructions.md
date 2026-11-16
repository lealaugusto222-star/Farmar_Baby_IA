# Instrucoes do projeto

- Mantenha a interface grafica em CustomTkinter separada do acesso ao banco de dados e das regras de negocio.
- Nunca armazene senhas em texto puro. Use hashing apropriado para senhas, como bcrypt ou hashlib com salt, e compare hashes de forma segura.
- Use consultas SQL parametrizadas com placeholders; nunca concatene dados do usuario em comandos SQL.
- Mantenha o codigo limpo e modular, seguindo os padroes existentes e usando docstrings curtas.
- Isole configuracao e acesso ao banco para facilitar testes e uma futura migracao entre SQLite e MySQL.
