# SPEC — Prova Backend IA / DOT

> Documento de especificação. **Fechar este doc antes de escrever código.**
> Objetivo: cobrir as 3 questões sem lacuna — modelo de dados, contratos, testes e critérios de aceitação definidos ANTES da implementação.

---

## 0. Visão geral

Prova técnica para a vaga **Desenvolvedor IA — RAGs (DOT)**. Três entregas independentes, reunidas num monorepo público no GitHub. Entrega = **link do repositório** colado no formulário (inhire). Prazo: 2 dias a partir de 08/06/2026.

As 3 questões somadas desenham um mini-stack de RAG: **API (Q1) + LLM conversacional (Q2) + busca semântica vetorial (Q3)**.

### Princípios de qualidade (não-negociáveis)
1. Todo código comentado explicando a lógica (exigência explícita do enunciado).
2. Toda questão roda standalone: `clone → instala requirements → roda`.
3. Testes unitários reais (não placeholder) onde o enunciado pede (Q1) e onde agrega valor (Q3).
4. Nenhuma dependência de credencial para Q1 e Q3. Só a Q2 precisa de `OPENAI_API_KEY`, lida de `.env`.
5. Zero código proprietário de terceiros (sem reaproveitar pipeline do SEO Empire — risco de vazamento + acoplamento). Conhecimento sim, código não.

---

## 1. Decisões técnicas globais

| Item | Decisão | Justificativa |
|------|---------|---------------|
| Linguagem | Python 3.11+ | Exigência da prova |
| Q1 Framework | **FastAPI** | Moderno, async, doc OpenAPI automática, alinhado a vaga de IA |
| Q1 ORM | SQLModel (SQLAlchemy + Pydantic) | Menos boilerplate, tipagem forte |
| Q1 Banco | SQLite | Exigência da prova |
| Q1 Testes | pytest + TestClient (httpx) | Padrão FastAPI |
| Q2 Orquestração | LangChain | Exigência da prova |
| Q2 LLM | OpenAI (gpt-4o-mini por custo, configurável) | Exigência; mini reduz custo de avaliação |
| Q3 Embeddings | **sentence-transformers** (`all-MiniLM-L6-v2`) | Local, grátis, offline — avaliador roda sem key |
| Q3 Vector store | **FAISS** (`faiss-cpu`) | Citado no enunciado, leve, sem servidor |
| Versionamento | Git + GitHub público | Entrega por link |
| Gestão de env | `.env` + `.env.example`, `python-dotenv` | Nunca commitar key |

### Estrutura do repositório
```
dot-prova-backend-ia/
├── README.md                  # visão geral + como rodar cada questão
├── SPEC.md                    # este documento
├── .gitignore                 # venv, .env, __pycache__, *.db, *.faiss
├── questao1_api_biblioteca/
│   ├── README.md
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # app FastAPI + rotas
│   │   ├── database.py        # engine SQLite + sessão
│   │   ├── models.py          # SQLModel: Livro
│   │   └── schemas.py         # Pydantic: entrada/saída
│   └── tests/
│       └── test_livros.py     # testes unitários dos endpoints
├── questao2_chatbot/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   ├── chatbot.py             # cadeia LangChain + OpenAI
│   └── exemplos.md            # perguntas/respostas demonstrativas
└── questao3_busca_semantica/
    ├── README.md
    ├── requirements.txt
    ├── data/
    │   └── documentos.json    # corpus de exemplo (posts de blog)
    ├── busca_semantica.py     # embeddings + FAISS + busca
    └── tests/
        └── test_busca.py      # testes de sanidade da busca
```

---

## 2. QUESTÃO 1 — API Biblioteca Virtual

### 2.1 Modelo de dados — `Livro`
| Campo | Tipo | Regras |
|-------|------|--------|
| `id` | int | PK, autoincrement |
| `titulo` | str | obrigatório, 1–255 chars |
| `autor` | str | obrigatório, 1–255 chars |
| `data_publicacao` | date | obrigatório, formato ISO `YYYY-MM-DD` |
| `resumo` | str | opcional, texto livre |

### 2.2 Endpoints (contrato)
| Método | Rota | Descrição | Body / Query | Resposta |
|--------|------|-----------|--------------|----------|
| `POST` | `/livros` | Cadastra livro | JSON `LivroCreate` | `201` + `Livro` |
| `GET` | `/livros` | Lista todos | — | `200` + `[Livro]` |
| `GET` | `/livros/{id}` | Busca por ID | path `id` | `200` + `Livro` / `404` |
| `GET` | `/livros/buscar` | Consulta por título OU autor | query `titulo?`, `autor?` | `200` + `[Livro]` |

- Busca por título/autor: **case-insensitive, match parcial** (`LIKE %termo%`).
- `/livros/buscar` sem nenhum parâmetro → `400` (ou retorna tudo — decisão: retorna `400` exigindo ao menos um filtro, mais explícito).
- Documentação automática via `/docs` (Swagger) e `/redoc`.

### 2.3 Casos de teste unitário (test_livros.py)
1. `test_cadastrar_livro_sucesso` — POST válido retorna 201 + corpo correto.
2. `test_cadastrar_livro_campos_faltando` — POST sem `titulo` retorna 422.
3. `test_cadastrar_data_invalida` — data fora do formato ISO retorna 422.
4. `test_listar_livros` — GET retorna lista com os livros cadastrados.
5. `test_buscar_por_titulo_parcial` — busca "senhor" acha "O Senhor dos Anéis".
6. `test_buscar_por_autor_case_insensitive` — "tolkien" acha "Tolkien".
7. `test_buscar_sem_filtro_retorna_400` — `/livros/buscar` sem query.
8. `test_buscar_id_inexistente_404` — GET `/livros/9999`.
- Fixture: banco SQLite **em memória** (`sqlite://`) recriado por teste — isolamento total, não suja o `.db` real.

### 2.4 Critérios de aceitação
- [ ] `uvicorn app.main:app` sobe sem erro.
- [ ] `/docs` mostra os 4 endpoints documentados.
- [ ] `pytest` passa 8/8 verde.
- [ ] Cadastro persiste no SQLite; consulta retorna o que foi gravado.

---

## 3. QUESTÃO 2 — Chatbot com IA Generativa (LangChain + OpenAI)

### 3.1 Comportamento
Chatbot de terminal (input/output de texto) que responde dúvidas sobre **programação em Python**. Usa LangChain pra orquestrar prompt → LLM → resposta.

### 3.2 Arquitetura da cadeia
```
input do usuário
   → ChatPromptTemplate (system: "tutor de Python didático" + history + pergunta)
   → ChatOpenAI (gpt-4o-mini, temperature 0.3)
   → StrOutputParser
   → resposta
```
- **Memória de conversa:** mantém histórico na sessão (lista de mensagens) pra perguntas de follow-up funcionarem.
- **System prompt:** posiciona como tutor de Python, respostas com explicação + exemplo de código.
- Config (`model`, `temperature`) no topo do arquivo, fácil de trocar.

### 3.3 Credenciais
- `OPENAI_API_KEY` lida de `.env` via `python-dotenv`.
- `.env.example` versionado; `.env` no `.gitignore`.
- Se a key faltar → mensagem de erro clara, não stacktrace cru.

### 3.4 Demonstração (exemplos.md)
- Pergunta 1: "Como criar uma lista em Python?" → resposta esperada (explicação + exemplo).
- Pergunta 2 (follow-up): "E como adicionar um item nela?" → testa a memória.
- Pergunta 3: "Qual a diferença entre lista e tupla?"

### 3.5 Critérios de aceitação
- [ ] `python chatbot.py` abre loop de conversa no terminal.
- [ ] Responde corretamente à pergunta-âncora do enunciado ("Como criar uma lista em Python?").
- [ ] Follow-up usa o histórico (memória funcionando).
- [ ] Sem key → erro amigável, não crash.
- [ ] `exemplos.md` com transcrições reais demonstrando o funcionamento.

> ⚠️ Esta é a única questão que custa (tokens OpenAI) pra rodar. Testamos com 2-3 perguntas pra capturar evidência no `exemplos.md`, depois o avaliador roda com a key dele.

---

## 4. QUESTÃO 3 — Busca Semântica (Embeddings + Vector Store)

### 4.1 Pipeline
```
documentos (JSON) → modelo embeddings (sentence-transformers)
   → vetores → índice FAISS (IndexFlatIP, normalizado = cosseno)
   → consulta → embedding da query → top-k por similaridade
```

### 4.2 Corpus de exemplo (`data/documentos.json`)
- ~10–15 documentos curtos, posts/artigos sobre temas variados (ex: Python, banco de dados, IA, web, devops) — variedade suficiente pra a busca discriminar relevância.
- Cada doc: `{ "id", "titulo", "texto" }`.

### 4.3 Decisões técnicas
- Modelo: `sentence-transformers/all-MiniLM-L6-v2` (384 dims, rápido, multilíngue razoável).
- Índice: `faiss.IndexFlatIP` com vetores **L2-normalizados** → produto interno = similaridade de cosseno.
- Função pública: `buscar(query: str, k: int = 3) -> list[dict]` retorna docs + score.
- Persistência opcional: salvar/carregar índice (`.faiss`) pra não re-embedar a cada execução.

### 4.4 Casos de teste (test_busca.py)
1. `test_busca_retorna_k_resultados` — `k=3` retorna 3 itens ordenados por score desc.
2. `test_busca_relevancia` — query "como usar listas em python" traz o doc de Python no topo, não o de devops.
3. `test_score_decrescente` — scores vêm em ordem decrescente.
- (Sem dependência de rede: modelo baixa uma vez e cacheia localmente.)

### 4.5 Critérios de aceitação
- [ ] `python busca_semantica.py "minha consulta"` imprime top-k relevante.
- [ ] Documentação inline do processo (embedding → store → busca).
- [ ] Demonstração com ≥2 consultas mostrando relevância coerente.
- [ ] `pytest` passa nos testes de sanidade.

---

## 5. Plano de Sprints

| Sprint | Escopo | Definition of Done |
|--------|--------|--------------------|
| **0 — Spec & esqueleto** | Este doc aprovado + estrutura de pastas + `.gitignore` + README raiz esqueleto | Spec fechada, repo init, primeiro commit |
| **1 — Q1 API** | FastAPI + SQLite + 4 endpoints + 8 testes | `pytest` 8/8 verde, `/docs` ok |
| **2 — Q3 Busca semântica** | Corpus + embeddings + FAISS + busca + 3 testes | Busca relevante demonstrada, testes verdes |
| **3 — Q2 Chatbot** | LangChain + OpenAI + memória + exemplos.md | Responde pergunta-âncora, evidência capturada |
| **4 — Polish & entrega** | README completo, revisão de comentários, push, gerar link | Repo público no ar, link pronto pro form |

### Ordem proposta: 1 → 3 → 2 (Q3 antes da Q2)
Q3 é onde há mais domínio prévio (fecha rápido) e não depende de credencial. Q2 por último por depender de key e custar tokens.

---

## 6. Riscos & mitigações

| Risco | Mitigação |
|-------|-----------|
| Vazar código proprietário do SEO Empire | Q3 escrita do zero, standalone. Só o know-how é reaproveitado. |
| Avaliador sem OpenAI key não roda Q2 | Q1 e Q3 rodam sem key; Q2 documentada + `exemplos.md` com evidência real |
| Download do modelo de embedding falha offline | README avisa que 1ª execução baixa ~80MB; cacheia depois |
| Key commitada por acidente | `.env` no `.gitignore` desde o commit 0; só `.env.example` versionado |
| `data_publicacao` com timezone/formato ambíguo | Contrato fixa ISO `YYYY-MM-DD`, validado por Pydantic |

---

## 7. Checklist de entrega final
- [ ] 3 questões implementadas e testadas
- [ ] README raiz + README por questão (como rodar)
- [ ] Testes passando (Q1 e Q3)
- [ ] `exemplos.md` da Q2 com evidência
- [ ] Nenhuma credencial commitada
- [ ] Repo público no GitHub
- [ ] Link colado no formulário inhire
