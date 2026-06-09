# Questão 2 — Chatbot de Python com LangChain + LLM

Chatbot de terminal que responde perguntas sobre programação em Python.
O fluxo de conversa é orquestrado pelo **LangChain**, e as respostas são
geradas por um **LLM** (OpenAI por padrão, conforme o enunciado). Mantém
**memória da conversa** para suportar perguntas de follow-up.

## Como rodar

```bash
cd questao2_chatbot
python -m venv venv && source venv/bin/activate   # opcional, recomendado
pip install -r requirements.txt

cp .env.example .env        # preencha OPENAI_API_KEY
python chatbot.py
```

Exemplo de conversa:

```
Você: Como criar uma lista em Python?
Bot: Em Python, uma lista é uma coleção ordenada e mutável... (explicação + exemplo)
```

Veja transcrições completas em [`exemplos.md`](./exemplos.md).

## Provedores de LLM

A cadeia é a mesma para qualquer provedor — todos implementam a interface
`BaseChatModel` do LangChain. Basta trocar a variável `LLM_PROVIDER`:

| `LLM_PROVIDER` | Modelo padrão | Chave necessária | Observação |
|----------------|---------------|------------------|------------|
| `openai` (padrão) | `gpt-4o-mini` | `OPENAI_API_KEY` | Caminho do enunciado |
| `groq` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | Free tier, sem cartão |
| `anthropic` | `claude-3-5-sonnet-latest` | `ANTHROPIC_API_KEY` | — |
| `fake` | — | nenhuma | Stub do LangChain, para testar a cadeia sem custo |

> Para usar `groq` ou `anthropic`, descomente a linha correspondente em
> `requirements.txt` e instale.

## Testes

```bash
pytest -v
```

Os testes rodam com o provedor `fake`, exercitando a **cadeia real**
(prompt → modelo → parser) sem consumir API nem exigir chave. Cobrem:
resposta da cadeia, acúmulo de histórico (memória), injeção do histórico no
prompt, provedor inválido e mensagem de erro amigável quando a chave falta.

Como todos os provedores compartilham a mesma interface do LangChain,
validar a cadeia com o `fake` garante que ela funciona igualmente com a
OpenAI — apenas o objeto do modelo muda.

## Arquitetura da cadeia

```
pergunta do usuário
   → ChatPromptTemplate  (system: tutor de Python + histórico + pergunta)
   → LLM                 (ChatOpenAI / ChatGroq / ...)
   → StrOutputParser
   → resposta
```

A memória é uma lista de mensagens (`HumanMessage`/`AIMessage`) injetada no
prompt via `MessagesPlaceholder` a cada turno, dando ao modelo o contexto
do diálogo.

## Estrutura

```
questao2_chatbot/
├── chatbot.py          # fábrica de LLM + cadeia + memória + loop CLI
├── .env.example        # configuração (provedor, modelo, chaves)
├── exemplos.md         # transcrições e respostas demonstrativas
└── tests/
    └── test_chatbot.py # testes da cadeia (com modelo fake)
```

## Decisões de projeto

- **Provider-agnostic**: a cadeia é desacoplada do provedor via uma fábrica
  (`get_llm`). Isso atende ao enunciado (OpenAI por padrão) e ainda permite
  rodar e testar sem custo (`fake`) ou com alternativas gratuitas (`groq`).
- **Falha cedo e clara**: se a chave do provedor não está definida, o
  programa avisa com instrução de correção em vez de estourar um stacktrace.
- **Memória explícita**: o histórico é mantido como lista de mensagens e
  reenviado a cada turno — simples de entender e de testar.
