# Farmar Baby IA

Aplicação desktop para apoio à organização e visualização de informações relacionadas ao acompanhamento da gestação. A interface é desenvolvida com CustomTkinter, e o acesso aos dados de usuários é isolado no módulo `banco.py`, com SQLite.

## Visão geral

O sistema oferece dois perfis:

- **Gestante:** pode criar uma conta, entrar no sistema e acessar o painel voltado ao acompanhamento da gestação.
- **Profissional:** pode criar uma conta mediante um código de autorização e acessar um painel próprio, com visualização de pacientes e informações de acompanhamento.

## Estrutura de arquivos

| Arquivo | Responsabilidade |
| --- | --- |
| `main.py` | Inicializa a janela principal e encaminha a navegação entre login, cadastro e painéis. |
| `login.py` | Apresenta a tela de login e direciona a pessoa autenticada ao painel correspondente ao seu perfil. |
| `cadastro.py` | Apresenta o cadastro, valida os dados informados e exige o código de autorização para o perfil profissional. |
| `dashboard.py` | Implementa o painel da gestante e suas seções de acompanhamento. |
| `dashboard_profissional.py` | Implementa o painel profissional e a visualização de pacientes e informações relacionadas. |
| `banco.py` | Centraliza a persistência SQLite, a criação da tabela de usuários, o cadastro, a autenticação e a geração/verificação de hashes de senha. |
| `ui_components.py` | Reúne componentes visuais reutilizáveis pelas telas da aplicação. |
| `farmar_baby.db` | Banco de dados SQLite criado ou utilizado na pasta do projeto. |
| `tests/` | Testes automatizados do banco, da autenticação, dos componentes visuais e da inicialização das telas. |

## Instalação e execução

1. Instale o Python e abra um terminal na pasta raiz do projeto.
2. (Opcional, recomendado) Crie e ative um ambiente virtual:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências:

   ```powershell
   pip install -r requirements.txt
   ```

4. Inicie a aplicação:

   ```powershell
   python main.py
   ```

O arquivo `farmar_baby.db` é armazenado na pasta do projeto. A tabela de usuários é criada automaticamente quando necessário.

## Cadastro profissional e código de convite

Para criar uma conta com o perfil **Profissional**, informe o código de autorização na tela de cadastro. Por padrão, o código é `FARMAR-PRO-2026`.

É possível substituir o valor padrão pela variável de ambiente `FARMAR_PROFISSIONAL_CODE`. No PowerShell, defina-a antes de iniciar a aplicação:

```powershell
$env:FARMAR_PROFISSIONAL_CODE = "seu-codigo-de-autorizacao"
python main.py
```

O código deve ser mantido em segredo e configurado por ambiente em implantações reais; o valor padrão é destinado à configuração atual do projeto.

## Banco de dados e senhas

A tabela `usuarios` contém os seguintes campos:

| Coluna | Tipo / restrições | Descrição |
| --- | --- | --- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identificador único do usuário. |
| `nome` | `TEXT NOT NULL` | Nome informado no cadastro. |
| `email` | `TEXT NOT NULL UNIQUE` | E-mail único usado para identificação e login. |
| `telefone` | `TEXT NOT NULL` | Telefone informado no cadastro. |
| `data_nasc` | `TEXT NOT NULL` | Data de nascimento armazenada como texto. |
| `senha_hash` | `TEXT NOT NULL` | Hash da senha; a senha em texto puro não é armazenada. |
| `tipo` | `TEXT NOT NULL DEFAULT 'gestante'` | Perfil do usuário: `gestante` ou `profissional`. |

As senhas são processadas com **PBKDF2-HMAC-SHA256**, usando um salt aleatório de 16 bytes e 100.000 iterações. O valor persistido em `senha_hash` combina o salt e o resultado hexadecimal, no formato `salt_hex:hash_hex`; a verificação compara os hashes de forma segura.

O módulo `banco.py` concentra as operações e usa consultas parametrizadas. A definição acima documenta o esquema atualmente esperado e serve de referência para uma futura integração ou migração do banco de dados.

## Testes automatizados

Com as dependências instaladas, execute a suíte a partir da raiz do projeto:

```powershell
pytest
```

Os testes incluem inicialização e destruição das telas gráficas; em ambientes sem suporte a interface gráfica, a inicialização pode depender da disponibilidade de um display.

## Aviso sobre dados de demonstração

Os dados clínicos, pacientes, consultas, sinais vitais, alertas e o monitoramento exibidos nos painéis estão em **modo de demonstração** e podem ser fictícios ou exemplos. Não são medições clínicas reais nem devem ser usados para decisões de saúde.
