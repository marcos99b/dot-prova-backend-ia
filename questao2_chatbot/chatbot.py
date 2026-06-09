"""
Chatbot de programação Python com LangChain + LLM (Questão 2).

O chatbot recebe perguntas do usuário via terminal e responde usando um
modelo de linguagem (LLM), com o fluxo de conversa orquestrado pelo
LangChain. Mantém memória da conversa para permitir perguntas de
follow-up.

Provedor do LLM (configurável por variável de ambiente LLM_PROVIDER):
  - openai     -> ChatOpenAI (PADRÃO, conforme o enunciado)
  - groq       -> ChatGroq (Llama 3.3, free tier)
  - anthropic  -> ChatAnthropic (Claude)
  - fake       -> modelo stub do LangChain, para testar a chain sem custo

A "chain" (prompt -> LLM -> parser) é IDÊNTICA para todos os provedores:
todos implementam a mesma interface do LangChain (BaseChatModel). Por isso,
validar a cadeia com qualquer um deles garante que ela funciona com a
OpenAI da mesma forma — só muda o objeto do modelo.

Uso:
    python chatbot.py
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()  # carrega variáveis do arquivo .env, se existir

# Prompt de sistema: posiciona o modelo como tutor de Python, pedindo
# respostas didáticas com explicação e exemplo de código.
SYSTEM_PROMPT = (
    "Você é um tutor especialista em programação Python. "
    "Responda de forma didática e objetiva, sempre em português. "
    "Quando fizer sentido, inclua um exemplo de código curto e comentado. "
    "Se a pergunta não for sobre programação, redirecione gentilmente o "
    "usuário para o tema de Python."
)

# Variável de ambiente que indica qual chave cada provedor precisa.
# Usada para dar uma mensagem de erro amigável quando a chave falta.
CHAVE_POR_PROVEDOR = {
    "openai": "OPENAI_API_KEY",
    "groq": "GROQ_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


def get_llm(provider: str, model: str | None = None, temperature: float = 0.3):
    """Fábrica de modelos: devolve o LLM do LangChain do provedor escolhido.

    O import de cada integração é feito dentro do ramo correspondente
    (lazy import), para que rodar com um provedor não exija ter as
    bibliotecas dos outros instaladas.
    """
    provider = provider.lower()

    if provider == "openai":
        # Caminho padrão exigido pelo enunciado.
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=model or "gpt-4o-mini", temperature=temperature)

    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(model=model or "llama-3.3-70b-versatile", temperature=temperature)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=model or "claude-3-5-sonnet-latest", temperature=temperature)

    if provider == "fake":
        # Modelo stub do próprio LangChain. Não consome API: serve para
        # validar a cadeia (prompt -> modelo -> parser) sem custo nem chave.
        from langchain_core.language_models.fake_chat_models import FakeListChatModel

        return FakeListChatModel(
            responses=[
                "Para criar uma lista em Python use colchetes: `frutas = ['maçã', 'uva']`.",
                "Use o método append: `frutas.append('banana')`.",
            ]
        )

    raise ValueError(
        f"Provedor desconhecido: '{provider}'. "
        f"Use um de: openai, groq, anthropic, fake."
    )


def construir_chain(llm):
    """Monta a cadeia LangChain: prompt (com histórico) -> LLM -> parser.

    O MessagesPlaceholder('historico') é o ponto onde a memória da conversa
    é injetada a cada chamada, permitindo perguntas de follow-up.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("historico"),
            ("human", "{pergunta}"),
        ]
    )
    # StrOutputParser extrai apenas o texto da resposta do modelo.
    return prompt | llm | StrOutputParser()


class Chatbot:
    """Encapsula a cadeia e o histórico da conversa.

    O histórico é uma lista de mensagens (HumanMessage/AIMessage) que cresce
    a cada turno e é reenviada ao modelo, dando a ele a memória do diálogo.
    """

    def __init__(self, llm) -> None:
        self.chain = construir_chain(llm)
        self.historico: list[BaseMessage] = []

    def responder(self, pergunta: str) -> str:
        """Processa uma pergunta, atualiza o histórico e devolve a resposta."""
        resposta = self.chain.invoke(
            {"pergunta": pergunta, "historico": self.historico}
        )
        # Guarda o turno (pergunta do usuário + resposta do bot) na memória.
        self.historico.append(HumanMessage(content=pergunta))
        self.historico.append(AIMessage(content=resposta))
        return resposta


def _validar_ambiente(provider: str) -> str | None:
    """Verifica se a chave de API do provedor está presente.

    Retorna uma mensagem de erro amigável se a chave faltar, ou None se
    estiver tudo certo. O provedor 'fake' não exige chave.
    """
    chave = CHAVE_POR_PROVEDOR.get(provider.lower())
    if chave and not os.getenv(chave):
        return (
            f"\n[erro] A variável {chave} não está definida.\n"
            f"Crie um arquivo .env (veja .env.example) e preencha {chave}, "
            f"ou rode com LLM_PROVIDER=fake para testar sem chave.\n"
        )
    return None


def main() -> None:
    """Loop de conversa no terminal."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("LLM_MODEL") or None
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # Falha cedo, com mensagem clara, se faltar a chave do provedor.
    erro = _validar_ambiente(provider)
    if erro:
        print(erro)
        return

    bot = Chatbot(get_llm(provider, model, temperature))

    print(f"Chatbot de Python (provedor: {provider}). Digite 'sair' para encerrar.\n")
    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break
        if not pergunta:
            continue
        resposta = bot.responder(pergunta)
        print(f"\nBot: {resposta}\n")


if __name__ == "__main__":
    main()
