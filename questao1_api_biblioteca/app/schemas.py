"""
Schemas de entrada e saída da API (camada de contrato HTTP).

Separar os schemas do modelo de tabela é uma boa prática: o cliente nunca
envia o `id` (ele é gerado pelo banco), e a resposta sempre o inclui.
Reaproveitamos `LivroBase` para herdar as mesmas validações dos campos.
"""

from app.models import LivroBase


class LivroCreate(LivroBase):
    """Corpo esperado no POST /livros.

    Idêntico à base: o cliente envia titulo, autor, data_publicacao e
    resumo (opcional). Não envia `id`.
    """

    pass


class LivroRead(LivroBase):
    """Formato devolvido pela API ao representar um livro.

    Acrescenta o `id` gerado pelo banco aos campos da base.
    """

    id: int
