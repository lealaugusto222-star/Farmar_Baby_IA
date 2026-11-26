# Instrucoes do projeto

- Mantenha a interface grafica em CustomTkinter separada do acesso ao banco de dados e das regras de negocio.
- Nunca armazene senhas em texto puro. Use exclusivamente o hashing PBKDF2 centralizado em `banco.py` para cadastro e autenticação, com salt aleatório e comparação segura.
- Use consultas SQL parametrizadas com placeholders; nunca concatene dados do usuario em comandos SQL.
- Mantenha o codigo limpo e modular, seguindo os padroes existentes e usando docstrings curtas.
- O projeto usa exclusivamente MySQL: mantenha a configuração e a criação de conexões centralizadas em `config_database.py`; não adicione SQLite, `DB_TYPE` ou fallback para outro banco.
- Não altere nem apague dados existentes no MySQL como efeito colateral da inicialização ou de outras operações.
- Sempre que alterar ou criar qualquer arquivo de interface grafica (`login.py`, `cadastro.py`, `ui_components.py`, `dashboard.py`, `dashboard_profissional.py`, `main.py`), você DEVE escrever e executar um teste automatizado que realmente instancie a janela/tela (e destrua logo em seguida com `.destroy()`) para garantir que nenhum erro de inicialização, layout ou `.bind()` passe despercebido antes de finalizar.
