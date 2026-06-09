# Exemplos de uso — Chatbot de Python

Este arquivo documenta o funcionamento do chatbot em dois níveis:

1. **Execução real da cadeia** (com o modelo `fake`, sem custo) — prova que
   o fluxo LangChain roda de ponta a ponta, incluindo a memória de conversa.
2. **Respostas ilustrativas de um LLM real** (OpenAI/Llama) — para mostrar a
   qualidade esperada das respostas quando uma chave de API está configurada.

---

## 1. Execução real da cadeia (provedor `fake`)

Comando:

```bash
LLM_PROVIDER=fake python chatbot.py
```

Transcrição real da execução:

```
Chatbot de Python (provedor: fake). Digite 'sair' para encerrar.

Você: Como criar uma lista em Python?
Bot: Para criar uma lista em Python use colchetes: `frutas = ['maçã', 'uva']`.

Você: E como adicionar um item nela?
Bot: Use o método append: `frutas.append('banana')`.

Você: sair
Até logo!
```

> O modelo `fake` devolve respostas pré-definidas, mas **a cadeia executada
> é a mesma** que roda com a OpenAI: o prompt é montado, o histórico é
> injetado, o modelo é invocado e a saída é parseada. Os testes em
> `tests/test_chatbot.py` confirmam que o histórico acumula corretamente
> entre os turnos (memória de conversa funcionando).

Comportamento quando falta a chave de API (provedor `openai` sem `OPENAI_API_KEY`):

```
[erro] A variável OPENAI_API_KEY não está definida.
Crie um arquivo .env (veja .env.example) e preencha OPENAI_API_KEY, ou
rode com LLM_PROVIDER=fake para testar sem chave.
```

---

## 2. Respostas ilustrativas com um LLM real

Configurando uma chave (`LLM_PROVIDER=openai` + `OPENAI_API_KEY`, ou
`LLM_PROVIDER=groq` + `GROQ_API_KEY`), as respostas têm a qualidade abaixo.

> As respostas a seguir ilustram a saída esperada de um LLM real para estas
> perguntas. O conteúdo é representativo: a pergunta-âncora do enunciado
> ("Como criar uma lista em Python?") é respondida com explicação + exemplo
> de código comentado, exatamente como o prompt de sistema instrui.

### Pergunta 1 — "Como criar uma lista em Python?"

> Em Python, uma lista é uma coleção ordenada e mutável de itens. Você cria
> uma lista escrevendo os elementos entre colchetes `[]`, separados por
> vírgula:
>
> ```python
> # Lista de frutas (strings)
> frutas = ["maçã", "banana", "uva"]
>
> # Lista vazia, para preencher depois
> numeros = []
>
> # Lista com tipos misturados é permitida
> variada = [1, "texto", 3.14, True]
>
> print(frutas[0])   # acessa o primeiro item -> "maçã"
> ```
>
> Você acessa os elementos pelo índice (começando em 0) e pode alterá-los a
> qualquer momento, já que listas são mutáveis.

### Pergunta 2 (follow-up) — "E como adicionar um item nela?"

> Para adicionar um item ao final da lista, use o método `append()`:
>
> ```python
> frutas = ["maçã", "banana"]
> frutas.append("laranja")      # adiciona no fim
> print(frutas)                 # ['maçã', 'banana', 'laranja']
>
> # Para inserir em uma posição específica, use insert(indice, item):
> frutas.insert(0, "abacaxi")   # insere no início
> ```
>
> O `append` é a forma mais comum; `insert` serve quando você precisa
> controlar a posição.

> Esta pergunta é um *follow-up*: ela depende do contexto da pergunta
> anterior (a lista `frutas`). A memória de conversa do chatbot é o que
> permite essa continuidade.

### Pergunta 3 — "Qual a diferença entre lista e tupla?"

> A principal diferença é a **mutabilidade**:
>
> - **Lista** (`[]`): mutável — você pode adicionar, remover e alterar itens.
> - **Tupla** (`()`): imutável — depois de criada, não muda.
>
> ```python
> lista = [1, 2, 3]
> lista[0] = 99          # OK: listas são mutáveis
>
> tupla = (1, 2, 3)
> # tupla[0] = 99        # ERRO: tuplas são imutáveis
> ```
>
> Use tuplas para dados que não devem mudar (mais seguras e levemente mais
> rápidas); use listas quando precisar modificar a coleção.
