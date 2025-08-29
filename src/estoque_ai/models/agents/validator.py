from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from src.estoque_ai.models.agents.models import llm_gemini
from src.estoque_ai.models.agents.route_checker import route_validator

template = """
Você é um agente especialista em APIs REST do eGestor.
Sua função é:
1. Receber a pergunta do usuário (`question`) e a rota da documentação (`selected_route`).
2. Gerar a `full_url` da rota.
3. Verificar se todos os parâmetros obrigatórios estão preenchidos:
- Se o parâmetro estiver presente na pergunta, inclua no `full_url`.
- Se não estiver presente, solicite explicitamente o valor ao usuário.

## Regras
- Use apenas parâmetros obrigatórios (required=true) e não-body (query, path, header, cookie).
- Se todos os parâmetros obrigatórios forem encontrados, retorne somente o JSON final com `full_url` e `parameters`.
- Se faltar algum parâmetro obrigatório, retorne o JSON com `"validated": false` e um campo `"missing_parameters"`
- Não suponha ou coloque parametros se não receber a rota com parametros obrigatorios.

listando os nomes dos parâmetros que precisam ser informados.

## Formato de Resposta
```json
{{
  "validated": true,
  "method": "POST",
  "path": "/categorias",
  "full_url": "https://v4.egestor.com.br/api/v1/produtos?codCategoria=123",
  "parameters": []
}}
## Se faltar parâmetro obrigatório:
{{
  "validated": false,
  "missing_parameters": ["codCategoria"]
}}
Pergunta do usuario:
{question}

Rota:
{route}
"""


def filter_validator(question):
    prompt = PromptTemplate(template=template, input_variables=['question', 'route'])

    route = route_validator(question)

    prompt_format = prompt.format(question=question, route=route)
    response = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response.content
