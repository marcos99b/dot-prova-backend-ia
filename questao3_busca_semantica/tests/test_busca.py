"""
Testes de sanidade da busca semântica (Questão 3).

Construir o índice carrega o modelo de embeddings (~80 MB na 1ª vez),
então o motor é montado uma única vez por sessão de teste via fixture
com escopo de módulo.
"""

import pytest

from busca_semantica import BuscaSemantica, carregar_documentos


@pytest.fixture(scope="module")
def motor() -> BuscaSemantica:
    """Monta o motor de busca uma vez para todos os testes do módulo."""
    documentos = carregar_documentos()
    return BuscaSemantica(documentos)


def test_busca_retorna_k_resultados(motor: BuscaSemantica):
    """A busca deve devolver exatamente k resultados."""
    resultados = motor.buscar("estruturas de dados em python", k=3)
    assert len(resultados) == 3
    # Cada resultado precisa carregar os campos esperados.
    for r in resultados:
        assert {"id", "titulo", "texto", "score"} <= r.keys()


def test_busca_relevancia(motor: BuscaSemantica):
    """Uma consulta sobre listas deve trazer o doc de listas no topo,
    e não um documento de tema distante como Docker."""
    resultados = motor.buscar("como criar e manipular listas em python", k=3)
    titulos = [r["titulo"] for r in resultados]
    assert "Listas em Python" in titulos
    # O documento mais relevante (posição 0) é o de listas.
    assert resultados[0]["titulo"] == "Listas em Python"
    # Tema não relacionado não deve aparecer no topo.
    assert "Containers com Docker" not in titulos


def test_score_decrescente(motor: BuscaSemantica):
    """Os scores devem vir ordenados do mais para o menos similar."""
    resultados = motor.buscar("busca por similaridade com vetores", k=5)
    scores = [r["score"] for r in resultados]
    assert scores == sorted(scores, reverse=True)


def test_k_maior_que_corpus(motor: BuscaSemantica):
    """Pedir mais resultados do que documentos não deve quebrar:
    retorna no máximo o tamanho do corpus."""
    total_docs = len(motor.documentos)
    resultados = motor.buscar("python", k=total_docs + 50)
    assert len(resultados) == total_docs
