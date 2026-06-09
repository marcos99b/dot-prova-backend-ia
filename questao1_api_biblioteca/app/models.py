"""
Modelos de dados (camada de persistência).

Usamos SQLModel, que combina SQLAlchemy (ORM) com Pydantic (validação),
permitindo definir a tabela e o schema de validação numa única classe.

A estratégia adotada segue o padrão recomendado pelo SQLModel:
  - LivroBase: campos compartilhados + regras de validação.
  - Livro:     a tabela em si (herda da base e adiciona o `id`).
Os schemas de entrada/saída da API ficam em `schemas.py`, reaproveitando
a mesma base para não duplicar as regras de validação.
"""

from datetime import date

from sqlmodel import Field, SQLModel


class LivroBase(SQLModel):
    """Campos comuns a todas as representações de um Livro.

    Concentrar as regras de validação aqui garante que tanto a tabela
    quanto o schema de criação (LivroCreate) usem exatamente os mesmos
    limites, sem repetição.
    """

    # Título do livro: obrigatório, entre 1 e 255 caracteres.
    # index=True acelera as consultas por título exigidas no enunciado.
    titulo: str = Field(min_length=1, max_length=255, index=True)

    # Autor: mesmas regras do título; indexado para busca rápida.
    autor: str = Field(min_length=1, max_length=255, index=True)

    # Data de publicação no formato ISO (YYYY-MM-DD).
    # O tipo `date` faz o Pydantic validar/parsear automaticamente.
    data_publicacao: date

    # Resumo é opcional (pode ser nulo).
    resumo: str | None = Field(default=None)


class Livro(LivroBase, table=True):
    """Tabela `livro` no banco SQLite.

    Herda todos os campos de LivroBase e acrescenta a chave primária.
    `table=True` é o que sinaliza ao SQLModel que esta classe vira tabela.
    """

    # Chave primária autoincremental. É None antes de persistir;
    # o banco atribui o valor no INSERT.
    id: int | None = Field(default=None, primary_key=True)
