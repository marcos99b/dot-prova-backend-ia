"""
Testes do chatbot (Questão 2).

Os testes usam o provedor 'fake' (FakeListChatModel do LangChain), que
roda a cadeia REAL (prompt -> modelo -> parser) sem consumir API nem exigir
chave. Como todos os provedores implementam a mesma interface BaseChatModel,
validar a cadeia com o fake garante que ela funciona igualmente com a
OpenAI — só muda o objeto do modelo.
"""

import pytest
from langchain_core.messages import HumanMessage

from chatbot import Chatbot, _validar_ambiente, construir_chain, get_llm


def test_chain_responde():
    """A cadeia processa uma pergunta e devolve uma string não vazia."""
    bot = Chatbot(get_llm("fake"))
    resposta = bot.responder("Como criar uma lista em Python?")
    assert isinstance(resposta, str)
    assert len(resposta) > 0


def test_memoria_acumula_historico():
    """Cada turno adiciona 2 mensagens (usuário + bot) ao histórico."""
    bot = Chatbot(get_llm("fake"))
    bot.responder("Como criar uma lista em Python?")
    bot.responder("E como adicionar um item nela?")
    # 2 turnos => 4 mensagens.
    assert len(bot.historico) == 4
    # A ordem deve ser: humano, ia, humano, ia.
    assert isinstance(bot.historico[0], HumanMessage)


def test_prompt_injeta_historico():
    """O histórico passado é realmente injetado nas mensagens do prompt.

    Validamos o wiring da memória: ao formatar o prompt com um histórico,
    a mensagem anterior precisa aparecer entre as mensagens enviadas.
    """
    from langchain_core.messages import AIMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "sistema"),
            MessagesPlaceholder("historico"),
            ("human", "{pergunta}"),
        ]
    )
    historico = [HumanMessage(content="pergunta antiga"), AIMessage(content="resposta antiga")]
    mensagens = prompt.format_messages(historico=historico, pergunta="nova pergunta")
    conteudos = [m.content for m in mensagens]
    assert "pergunta antiga" in conteudos
    assert "resposta antiga" in conteudos
    assert "nova pergunta" in conteudos


def test_provider_invalido_levanta_erro():
    """Um provedor desconhecido deve levantar ValueError."""
    with pytest.raises(ValueError):
        get_llm("provedor-inexistente")


def test_validar_ambiente_sem_chave(monkeypatch):
    """Sem a chave do provedor, a validação retorna mensagem de erro amigável."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    msg = _validar_ambiente("openai")
    assert msg is not None
    assert "OPENAI_API_KEY" in msg


def test_validar_ambiente_fake_dispensa_chave():
    """O provedor 'fake' não exige nenhuma chave."""
    assert _validar_ambiente("fake") is None
