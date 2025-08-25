import os

import requests
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from models import llm_gemini
from validator import filter_validator

load_dotenv()


"""
Não está sendo usado
"""


template = """
Você é o quarto agente de um sistema inteligente integrado ao ERP eGestor. Sua função é executar a consulta na API usando as informações validadas pelos agentes anteriores e retornar a resposta em formato JSON.
Sua função é consultar a rota que você recebera alem da rota você recebera o access_token que é obrigatorio para executar a consulta

# 2️⃣ Usar o access_token para acessar os produtos
produtos_url = "https://v4.egestor.com.br/api/v1/produtos"
headers = {{
    "Authorization": f"Bearer {{access_token}}"
}}

retorne apenas o json com os dados adiquiridos atraves da api.

rota:
{route}

toke de acesso:
{access_token}

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


def route_executor(question):
    prompt = PromptTemplate(template=template, input_variables=['access_token', 'route'])

    access_token = get_token()
    route = filter_validator(question)

    if route.get('validated') is not True:
        return route

    if route.get('method') != 'GET':
        return route.get('method')

    full_url = route.get('full_url')
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(full_url, headers=headers)
    response.raise_for_status()

    prompt_format = prompt.format(access_token=access_token, route=route)
    response_format = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response_format.content


r = route_executor(question='quantos produtos tem?')
print(r)
