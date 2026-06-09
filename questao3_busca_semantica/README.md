# Questão 3 — Busca Semântica com Embeddings e Vector Store

Sistema de busca semântica de documentos: dado um texto de consulta,
retorna os documentos mais relevantes **por significado** (não por
palavra-chave exata), usando embeddings e uma vector store FAISS.

> **Não requer chave de API.** Os embeddings são gerados localmente com
> `sentence-transformers`, então o avaliador clona e roda direto.

## Pipeline

```
documentos (JSON)
   → embeddings (sentence-transformers, all-MiniLM-L6-v2)
   → índice FAISS (IndexFlatIP, vetores normalizados = cosseno)
   → consulta → embedding da consulta → top-k mais similares
```

## Como rodar

```bash
cd questao3_busca_semantica
python -m venv venv && source venv/bin/activate   # opcional, recomendado
pip install -r requirements.txt

python busca_semantica.py "como usar listas em python"
python busca_semantica.py "indexar embeddings para recuperar documentos similares" --k 3
```

> A primeira execução baixa o modelo de embeddings (~80 MB) e o mantém em
> cache local; as próximas são instantâneas.

## Exemplo de saída

```
Consulta: "indexar embeddings para recuperar documentos similares"
------------------------------------------------------------
1. [0.544] Vector stores e busca por similaridade
   Vector stores como FAISS indexam vetores para recuperar rapidamente os mais próximos de uma consulta...
2. [0.390] Embeddings e representação vetorial de texto
   Embeddings convertem texto em vetores numéricos densos que capturam significado semântico...
3. [0.314] APIs REST e métodos HTTP
   APIs REST expõem recursos por meio de URLs e métodos HTTP...
```

A busca entende **significado**: a consulta acima traz os documentos sobre
*vector stores* e *embeddings* no topo, mesmo sem repetir as palavras
exatas do texto. Outro exemplo — `"como tratar erros que quebram o
programa"` retorna o documento de *tratamento de exceções* em primeiro,
ainda que a consulta não use a palavra "exceção".

## Testes

```bash
pytest -v
```

Cobrem: retorno de exatamente k resultados com os campos certos,
relevância (o documento correto vem no topo), ordenação por score
decrescente e robustez quando k é maior que o corpus.

## Como funciona (detalhe técnico)

- **Embeddings normalizados**: cada vetor é normalizado (norma L2 = 1).
  Assim o produto interno usado pelo FAISS equivale à **similaridade de
  cosseno**, a métrica padrão para comparar significado de textos.
- **FAISS `IndexFlatIP`**: busca exata por produto interno. Para o tamanho
  deste corpus é ideal; para milhões de vetores trocaria-se por um índice
  aproximado (ex.: IVF ou HNSW) sem mudar a interface de busca.
- **Corpus**: `data/documentos.json` traz 12 documentos curtos de temas
  variados (Python, bancos de dados, DevOps, IA) para a busca ter o que
  discriminar em termos de relevância.

## Estrutura

```
questao3_busca_semantica/
├── busca_semantica.py      # embeddings + FAISS + função de busca + CLI
├── data/
│   └── documentos.json     # corpus de exemplo
└── tests/
    └── test_busca.py       # testes de sanidade
```
