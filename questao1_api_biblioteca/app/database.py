"""
Configuração do banco de dados (camada de infraestrutura).

Centraliza a criação do engine SQLite, a criação das tabelas e o
fornecimento de sessões via injeção de dependência do FastAPI.
"""

from sqlmodel import Session, SQLModel, create_engine

# Banco SQLite gravado em arquivo no diretório de execução.
# (exigência do enunciado: usar SQLite para armazenamento)
DATABASE_URL = "sqlite:///biblioteca.db"

# check_same_thread=False é necessário porque o FastAPI pode atender
# requisições em threads diferentes da que abriu a conexão SQLite.
connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)


def criar_db_e_tabelas() -> None:
    """Cria o arquivo do banco e todas as tabelas mapeadas (se ainda não existirem).

    Chamado uma vez no startup da aplicação.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependência do FastAPI que entrega uma sessão por requisição.

    O `yield` garante que a sessão seja fechada ao fim do request,
    mesmo em caso de erro. Nos testes, esta dependência é substituída
    por uma sessão apontando para um banco em memória.
    """
    with Session(engine) as session:
        yield session
