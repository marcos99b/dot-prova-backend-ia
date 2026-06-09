# Questão 1 — API de Biblioteca Virtual

API REST para cadastrar e consultar livros, construída com **FastAPI** e
persistência em **SQLite** via **SQLModel**. Inclui testes unitários com pytest.

## Como rodar

```bash
cd questao1_api_biblioteca
python -m venv venv && source venv/bin/activate   # opcional, recomendado
pip install -r requirements.txt

# Sobe a API (documentação interativa em http://localhost:8000/docs)
uvicorn app.main:app --reload
```

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/livros` | Cadastra um livro |
| `GET` | `/livros` | Lista todos os livros |
| `GET` | `/livros/buscar?titulo=&autor=` | Consulta por título e/ou autor (parcial, case-insensitive) |
| `GET` | `/livros/{id}` | Busca um livro por ID |

### Exemplos (curl)

```bash
# Cadastrar
curl -X POST http://localhost:8000/livros \
  -H "Content-Type: application/json" \
  -d '{"titulo":"O Senhor dos Anéis","autor":"J.R.R. Tolkien","data_publicacao":"1954-07-29","resumo":"Uma jornada para destruir o Um Anel."}'

# Listar
curl http://localhost:8000/livros

# Buscar por autor
curl "http://localhost:8000/livros/buscar?autor=tolkien"

# Buscar por título
curl "http://localhost:8000/livros/buscar?titulo=senhor"
```

## Testes

```bash
pytest -v
```

São 8 testes cobrindo: cadastro com sucesso, validação de campos
obrigatórios, validação de data, listagem, busca por título parcial,
busca por autor case-insensitive, busca sem filtro (400) e ID
inexistente (404). Cada teste roda contra um SQLite **em memória**, sem
tocar o banco real.

## Estrutura

```
questao1_api_biblioteca/
├── app/
│   ├── main.py        # aplicação FastAPI + rotas
│   ├── database.py    # engine SQLite + sessão
│   ├── models.py      # modelo de tabela (Livro)
│   └── schemas.py     # schemas de entrada/saída
└── tests/
    └── test_livros.py # testes unitários dos endpoints
```

## Decisões de projeto

- **SQLModel** une ORM (SQLAlchemy) e validação (Pydantic) numa só
  definição, reduzindo duplicação entre modelo de tabela e schema.
- A rota `/livros/buscar` é declarada antes de `/livros/{id}` para evitar
  conflito de rota (o termo "buscar" não pode ser confundido com um ID).
- Busca exige ao menos um filtro e retorna **400** caso contrário — torna
  o contrato explícito em vez de devolver a base inteira silenciosamente.
