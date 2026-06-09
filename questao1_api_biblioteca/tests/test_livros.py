"""
Testes unitários dos endpoints da API de biblioteca (Questão 1).

Estratégia de isolamento:
  - Cada teste roda contra um banco SQLite EM MEMÓRIA, recriado do zero.
  - A dependência `get_session` da aplicação é sobrescrita para usar essa
    sessão de teste, então o banco real (biblioteca.db) nunca é tocado.
  - Usamos StaticPool para que a mesma conexão em memória seja reutilizada
    dentro do teste (caso contrário cada conexão veria um banco vazio).
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    """Cria um banco SQLite em memória isolado por teste."""
    engine = create_engine(
        "sqlite://",  # "" = banco em memória
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Cria um TestClient com a dependência de sessão sobrescrita.

    Não usamos o TestClient como context manager de propósito: assim o
    lifespan da app (que criaria o biblioteca.db real) não é disparado.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# Payload base reutilizado em vários testes.
LIVRO_VALIDO = {
    "titulo": "O Senhor dos Anéis",
    "autor": "J.R.R. Tolkien",
    "data_publicacao": "1954-07-29",
    "resumo": "Uma jornada para destruir o Um Anel.",
}


def test_cadastrar_livro_sucesso(client: TestClient):
    """POST /livros com dados válidos retorna 201 e o livro criado."""
    resp = client.post("/livros", json=LIVRO_VALIDO)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] is not None
    assert body["titulo"] == LIVRO_VALIDO["titulo"]
    assert body["autor"] == LIVRO_VALIDO["autor"]
    assert body["data_publicacao"] == LIVRO_VALIDO["data_publicacao"]


def test_cadastrar_livro_campos_faltando(client: TestClient):
    """POST sem o campo obrigatório 'titulo' retorna 422 (validação)."""
    payload = {k: v for k, v in LIVRO_VALIDO.items() if k != "titulo"}
    resp = client.post("/livros", json=payload)
    assert resp.status_code == 422


def test_cadastrar_data_invalida(client: TestClient):
    """POST com data fora do formato ISO retorna 422."""
    payload = {**LIVRO_VALIDO, "data_publicacao": "29/07/1954"}
    resp = client.post("/livros", json=payload)
    assert resp.status_code == 422


def test_listar_livros(client: TestClient):
    """GET /livros retorna a lista com os livros cadastrados."""
    client.post("/livros", json=LIVRO_VALIDO)
    client.post(
        "/livros",
        json={
            "titulo": "O Hobbit",
            "autor": "J.R.R. Tolkien",
            "data_publicacao": "1937-09-21",
            "resumo": "Bilbo parte em uma aventura inesperada.",
        },
    )
    resp = client.get("/livros")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_buscar_por_titulo_parcial(client: TestClient):
    """Busca por termo parcial do título encontra o livro."""
    client.post("/livros", json=LIVRO_VALIDO)
    resp = client.get("/livros/buscar", params={"titulo": "senhor"})
    assert resp.status_code == 200
    resultados = resp.json()
    assert len(resultados) == 1
    assert resultados[0]["titulo"] == LIVRO_VALIDO["titulo"]


def test_buscar_por_autor_case_insensitive(client: TestClient):
    """Busca por autor ignora maiúsculas/minúsculas."""
    client.post("/livros", json=LIVRO_VALIDO)
    resp = client.get("/livros/buscar", params={"autor": "tolkien"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_buscar_sem_filtro_retorna_400(client: TestClient):
    """GET /livros/buscar sem nenhum filtro retorna 400."""
    resp = client.get("/livros/buscar")
    assert resp.status_code == 400


def test_buscar_id_inexistente_404(client: TestClient):
    """GET /livros/{id} para ID inexistente retorna 404."""
    resp = client.get("/livros/9999")
    assert resp.status_code == 404
