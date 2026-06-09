"""
API REST de Biblioteca Virtual (Questão 1).

Permite cadastrar e consultar livros. Construída com FastAPI, persistindo
em SQLite via SQLModel. A documentação interativa é gerada automaticamente
em /docs (Swagger) e /redoc.

Endpoints:
    POST   /livros          -> cadastra um livro
    GET    /livros          -> lista todos os livros
    GET    /livros/buscar   -> consulta por título e/ou autor (match parcial)
    GET    /livros/{id}     -> busca um livro por ID
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, col, select

from app.database import criar_db_e_tabelas, get_session
from app.models import Livro
from app.schemas import LivroCreate, LivroRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação.

    No startup, garante que o banco e as tabelas existam antes de
    atender qualquer requisição.
    """
    criar_db_e_tabelas()
    yield


app = FastAPI(
    title="Biblioteca Virtual API",
    description="API para cadastro e consulta de livros (Questão 1 — Prova Backend IA / DOT).",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post(
    "/livros",
    response_model=LivroRead,
    status_code=201,
    summary="Cadastrar livro",
    tags=["livros"],
)
def cadastrar_livro(
    livro: LivroCreate,
    session: Session = Depends(get_session),
) -> Livro:
    """Cadastra um novo livro.

    O corpo é validado pelo schema `LivroCreate` (título e autor
    obrigatórios, data em formato ISO). Retorna o livro criado já com
    o `id` atribuído pelo banco e status HTTP 201 (Created).
    """
    # Converte o schema de entrada no modelo de tabela.
    db_livro = Livro.model_validate(livro)
    session.add(db_livro)
    session.commit()
    session.refresh(db_livro)  # recarrega para popular o `id` gerado
    return db_livro


@app.get(
    "/livros",
    response_model=list[LivroRead],
    summary="Listar todos os livros",
    tags=["livros"],
)
def listar_livros(session: Session = Depends(get_session)) -> list[Livro]:
    """Retorna todos os livros cadastrados."""
    return list(session.exec(select(Livro)).all())


# IMPORTANTE: esta rota precisa ser declarada ANTES de "/livros/{livro_id}".
# Caso contrário, o FastAPI tentaria interpretar "buscar" como um {livro_id}
# e a requisição falharia. A ordem de declaração resolve a ambiguidade.
@app.get(
    "/livros/buscar",
    response_model=list[LivroRead],
    summary="Consultar livros por título ou autor",
    tags=["livros"],
)
def buscar_livros(
    titulo: str | None = Query(default=None, description="Termo (parcial) do título"),
    autor: str | None = Query(default=None, description="Termo (parcial) do autor"),
    session: Session = Depends(get_session),
) -> list[Livro]:
    """Consulta livros por título e/ou autor.

    A busca é case-insensitive e por correspondência parcial (LIKE %termo%).
    É obrigatório informar ao menos um dos filtros; sem nenhum, retorna 400
    para deixar explícito que a consulta precisa de um critério.
    """
    if not titulo and not autor:
        raise HTTPException(
            status_code=400,
            detail="Informe ao menos um filtro: 'titulo' ou 'autor'.",
        )

    query = select(Livro)
    if titulo:
        # col() expõe os operadores de coluna do SQLAlchemy de forma
        # type-safe; ilike faz a comparação case-insensitive.
        query = query.where(col(Livro.titulo).ilike(f"%{titulo}%"))
    if autor:
        query = query.where(col(Livro.autor).ilike(f"%{autor}%"))

    return list(session.exec(query).all())


@app.get(
    "/livros/{livro_id}",
    response_model=LivroRead,
    summary="Buscar livro por ID",
    tags=["livros"],
)
def obter_livro(
    livro_id: int,
    session: Session = Depends(get_session),
) -> Livro:
    """Retorna um livro pelo seu ID, ou 404 se não existir."""
    livro = session.get(Livro, livro_id)
    if livro is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return livro
