from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

import requests
import os
from dotenv import load_dotenv

from models import llm_gemini
from filter_checker import filter_validator

load_dotenv()


template = """
# Prompt para Quarto Agente - Executor de Consultas ERP

Você é o quarto agente de um sistema inteligente integrado ao ERP eGestor.  
Sua função é **executar a consulta na API** usando as informações validadas pelos agentes anteriores e **retornar a resposta em formato JSON puro**.

## Instruções:
1. Você receberá:
   - **Rota da API** (`{{route}}`)
   - **Access Token** (`{{access_token}}`) — obrigatório para autenticação
   - (Opcional) **Parâmetros de consulta** — se aplicável à rota

2. **Regra obrigatória sobre parâmetros**:  
   - Se algum parâmetro essencial para a execução da consulta estiver **faltando**, você **não deve tentar executar a requisição**.
   - Neste caso, retorne um JSON no seguinte formato:
     ```json
     {{
       "erro": "Parâmetros ausentes",
       "parametros_faltantes": ["nome_do_parametro1", "nome_do_parametro2"]
     }}
     ```

3. **Execução da consulta**:
   - Utilize o `access_token` no header de autenticação:
     ```json
     headers = {{
         "Authorization": f"Bearer {{access_token}}"
     }}
     ```
   - Realize a requisição para a rota informada.
   - **Não adicione comentários ou texto fora do JSON final**.

## Exemplo de consulta:
```json
produtos_url = "https://v4.egestor.com.br/api/v1/produtos"
headers = {{
    "Authorization": f"Bearer {{access_token}}"
}}

rota:
{route}

toke de acesso:
{access_token}

"""


def get_token():
    API_KEY = os.getenv("API_ERP")
    auth_url = os.getenv("AUTH_URL")

    auth_body = {
        "grant_type": "personal",
        "personal_token": API_KEY
    }

    auth_response = requests.post(auth_url, json=auth_body)
    auth_response.raise_for_status()

    token_data = auth_response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise ValueError("Não foi possível obter o access_token. Verifique sua chave API.")

    return access_token



def route_executor(question):
    access_token = get_token()
    route = filter_validator(question)

    prompt = PromptTemplate(
        template=template,
        input_variables=["access_token", "route"]
    )


    prompt_format = prompt.format(access_token=access_token, route=route)
    response = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response.content

token = route_executor('tem alguma NF?')
print(token)