"""
Busca semântica de documentos (Questão 3).

Pipeline:
    documentos (JSON)
        -> embeddings (sentence-transformers, modelo local)
        -> índice FAISS (similaridade de cosseno)
        -> consulta -> top-k documentos mais relevantes

Por que rodar local (sentence-transformers) em vez de uma API paga:
o avaliador consegue clonar e executar sem precisar de nenhuma chave de
API. O modelo `all-MiniLM-L6-v2` (384 dimensões) é leve e baixado uma
única vez (~80 MB), ficando em cache para as próximas execuções.

Uso pela linha de comando:
    python busca_semantica.py "como usar listas em python"
    python busca_semantica.py "armazenar vetores para busca" --k 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Caminho do corpus e nome do modelo de embeddings.
CAMINHO_DOCUMENTOS = Path(__file__).parent / "data" / "documentos.json"
NOME_MODELO = "all-MiniLM-L6-v2"


class BuscaSemantica:
    """Encapsula o modelo de embeddings, o índice FAISS e a busca.

    A construção é feita uma vez (carrega modelo, gera embeddings e monta
    o índice); depois, cada chamada a `buscar` é apenas embedar a consulta
    e procurar os vizinhos mais próximos.
    """

    def __init__(self, documentos: list[dict], nome_modelo: str = NOME_MODELO) -> None:
        self.documentos = documentos
        # Carrega o modelo de embeddings (baixa do hub na 1ª vez, depois cacheia).
        self.modelo = SentenceTransformer(nome_modelo)
        # Constrói o índice FAISS a partir dos textos dos documentos.
        self.indice = self._construir_indice()

    def _embedar(self, textos: list[str]) -> np.ndarray:
        """Gera embeddings normalizados (L2) para uma lista de textos.

        Normalizar os vetores faz com que o produto interno (usado pelo
        índice) seja equivalente à similaridade de cosseno — a métrica
        padrão para comparar significado de textos.
        """
        embeddings = self.modelo.encode(
            textos,
            convert_to_numpy=True,
            normalize_embeddings=True,  # deixa cada vetor com norma 1
        )
        return embeddings.astype("float32")  # FAISS exige float32

    def _construir_indice(self) -> faiss.IndexFlatIP:
        """Cria um índice FAISS de produto interno com os embeddings do corpus.

        IndexFlatIP faz busca exata por produto interno; como os vetores
        estão normalizados, isso equivale à similaridade de cosseno.
        """
        textos = [doc["texto"] for doc in self.documentos]
        embeddings = self._embedar(textos)

        dimensao = embeddings.shape[1]
        indice = faiss.IndexFlatIP(dimensao)
        indice.add(embeddings)
        return indice

    def buscar(self, consulta: str, k: int = 3) -> list[dict]:
        """Retorna os k documentos mais semanticamente próximos da consulta.

        Cada resultado inclui os dados do documento e o `score` de
        similaridade (cosseno, entre -1 e 1; quanto maior, mais relevante).
        """
        # Garante que k não ultrapasse o número de documentos disponíveis.
        k = min(k, len(self.documentos))

        # Embeda a consulta (mesmo processo dos documentos).
        emb_consulta = self._embedar([consulta])

        # FAISS devolve os scores e os índices dos k vizinhos mais próximos,
        # já ordenados do mais para o menos similar.
        scores, indices = self.indice.search(emb_consulta, k)

        resultados: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            doc = self.documentos[idx]
            resultados.append(
                {
                    "id": doc["id"],
                    "titulo": doc["titulo"],
                    "texto": doc["texto"],
                    "score": float(score),
                }
            )
        return resultados


def carregar_documentos(caminho: Path = CAMINHO_DOCUMENTOS) -> list[dict]:
    """Lê o corpus de documentos do arquivo JSON."""
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def _formatar_resultados(consulta: str, resultados: list[dict]) -> str:
    """Monta uma saída legível para o terminal."""
    linhas = [f'\nConsulta: "{consulta}"', "-" * 60]
    for pos, r in enumerate(resultados, start=1):
        linhas.append(f"{pos}. [{r['score']:.3f}] {r['titulo']}")
        linhas.append(f"   {r['texto']}")
    return "\n".join(linhas)


def main() -> None:
    """Ponto de entrada CLI: recebe a consulta e imprime os top-k resultados."""
    parser = argparse.ArgumentParser(description="Busca semântica de documentos.")
    parser.add_argument("consulta", help="Texto da consulta")
    parser.add_argument("--k", type=int, default=3, help="Número de resultados (padrão: 3)")
    args = parser.parse_args()

    documentos = carregar_documentos()
    motor = BuscaSemantica(documentos)
    resultados = motor.buscar(args.consulta, k=args.k)
    print(_formatar_resultados(args.consulta, resultados))


if __name__ == "__main__":
    main()
