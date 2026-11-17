# Instrucoes do projeto

- Mantenha a interface grafica em CustomTkinter separada do acesso ao banco de dados e das regras de negocio.
- Nunca armazene senhas em texto puro. Use hashing apropriado para senhas, como bcrypt ou hashlib com salt, e compare hashes de forma segura.
- Use consultas SQL parametrizadas com placeholders; nunca concatene dados do usuario em comandos SQL.
- Mantenha o codigo limpo e modular, seguindo os padroes existentes e usando docstrings curtas.
- Isole configuracao e acesso ao banco para facilitar testes e uma futura migracao entre SQLite e MySQL.
- Sempre que alterar ou criar qualquer arquivo de interface grafica (`login.py`, `cadastro.py`, `ui_components.py`, `dashboard.py`, `dashboard_profissional.py`, `main.py`), você DEVE escrever e executar um teste automatizado que realmente instancie a janela/tela (e destrua logo em seguida com `.destroy()`) para garantir que nenhum erro de inicialização, layout ou `.bind()` passe despercebido antes de finalizar.
