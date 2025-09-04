import json
import os

import requests
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from estoque_ai.models.agents.models import llm_gemini
from estoque_ai.models.agents.validator import filter_validator

load_dotenv()

cache = {}
template = """
Você é um agente que recebe:
- A pergunta feita pelo usuário.
- A resposta da API em formato JSON.
Sua tarefa:
Transformar esses dados em uma resposta natural e útil, escrita em português simples.
##Regras
Seja direto e objetivo.
Use números e valores exatos quando existirem.
Para listas grandes Informe todos apenas se for pedido. Senão apenas responda com numeros.
Se você receber um json com:
falta de parâmetro obrigatório:
{{
  "validated": false,
  "missing_parameters": ["codCategoria"]
}}

Se faltar parametro ("missing_parameters"), explique claramente o que está faltando e peça de forma amigável.
Se houver erro, explique em linguagem simples e sugira tentar de novo.
Se for algo relacionado ao produto e o usuário perguntar algo sobre os materiais utilizados na produção do produto, consulte a informação dentro de anotações internas (ela armazena um JSON da ficha técnica do produto)
Se receber uma lista de conversa como pergunta, Analize o contexto e responda a ultima pergunta.

Em caso de erro de autenticação:
Dados: {{ "error": "authentication_error" }}
Resposta: "Não consegui acessar os dados agora por um problema de autenticação. Tente novamente em alguns minutos."

## O Que Não Fazer
- Não use formatação markdown (*, **, #, etc.)
- Não inclua códigos JSON na resposta final
- Não use termos técnicos desnecessários
- Não inclua barras invertidas ou aspas extras
- Não copie estruturas JSON literalmente

## Formato da Resposta
Sempre retorne apenas o texto formatado, limpo e humanizado, sem qualquer estrutura JSON ou formatação especial e sem quebra de linha (\n).

Aqui está o que o usuário perguntou:
{question}

Aqui está a resposta do sistema:
{response_json}

"""


def get_token():
    API_KEY = os.getenv('API_ERP')
    auth_url = os.getenv('AUTH_URL')

    auth_body = {'grant_type': 'personal', 'personal_token': API_KEY}

    auth_response = requests.post(auth_url, json=auth_body)
    auth_response.raise_for_status()

    token_data = auth_response.json()
    access_token = token_data.get('access_token')

    if not access_token:
        raise ValueError('Não foi possível obter o access_token. Verifique sua chave API.')

    return access_token


def route_executor(question, history):
    prompt = PromptTemplate(template=template, input_variables=['question', 'response_json'])

    access_token = get_token()
    # Valida rota com agente anterior
    route = filter_validator(question)
    validation = route.strip('```json').strip('```').strip()
    route_validation = json.loads(validation)

    if route_validation['validated'] is not True:
        response = {'erro': 'Rota não validada', 'detalhes': route_validation}

    elif route_validation['method'] != 'GET':
        method = route_validation['route']['method']
        response = {'erro': 'Método não suportado', 'metodo': method}

    full_url = route_validation.get('full_url')
    if full_url and full_url in cache:
        response = cache[full_url]

    else:
        response = requests.get(url=route_validation['full_url'], headers={'Authorization': f'Bearer {access_token}'})
        response = response.json()
        cache[route_validation['full_url']] = response

    prompt_format = prompt.format(question=question, response_json=response, history=history)
    response_format = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response_format.content
