# Prova Backend IA — DOT

Resolução da avaliação técnica para a vaga **Desenvolvedor IA (RAGs)**. Três entregas independentes em Python, cada uma em sua pasta, rodando standalone.

> Especificação completa do projeto (modelo de dados, contratos, casos de teste, critérios de aceitação): ver [`SPEC.md`](./SPEC.md).

## Estrutura

| Pasta | Questão | Stack |
|-------|---------|-------|
| [`questao1_api_biblioteca/`](./questao1_api_biblioteca) | API de biblioteca virtual (CRUD + busca) | FastAPI · SQLModel · SQLite · pytest |
| [`questao2_chatbot/`](./questao2_chatbot) | Chatbot de Python com LLM | LangChain · OpenAI |
| [`questao3_busca_semantica/`](./questao3_busca_semantica) | Busca semântica de documentos | sentence-transformers · FAISS |

## Como rodar

Cada questão tem o próprio `README.md` e `requirements.txt`. Em resumo:

```bash
# Questão 1 — API
cd questao1_api_biblioteca
pip install -r requirements.txt
uvicorn app.main:app --reload      # docs em http://localhost:8000/docs
pytest

# Questão 3 — Busca semântica (não precisa de API key)
cd questao3_busca_semantica
pip install -r requirements.txt
python busca_semantica.py "como usar listas em python"
pytest

# Questão 2 — Chatbot (precisa de OPENAI_API_KEY)
cd questao2_chatbot
pip install -r requirements.txt
cp .env.example .env                # preencher OPENAI_API_KEY
python chatbot.py
```

## Requisitos
- Python 3.11+
- Apenas a **Questão 2** requer uma `OPENAI_API_KEY`. Questões 1 e 3 rodam sem nenhuma credencial.

## Autor
Marcos Antônio de Albuquerque Filho
