from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

import requests
import os
import json
from dotenv import load_dotenv

from models import llm_gemini
from validator import filter_validator

load_dotenv()


template = """
Você é um agente que recebe:

A pergunta feita pelo usuário.

A resposta da API em formato JSON.

Sua tarefa

Transformar esses dados em uma resposta natural e útil, escrita em português simples, sem mostrar JSON, sem usar markdown, sem aspas ou barras desnecessárias.

Regras

Seja direto e objetivo.

Use números e valores exatos quando existirem.

Para listas grandes, diga a quantidade e cite alguns exemplos.

Se faltar informação, explique claramente o que está faltando e peça de forma amigável.

Se houver erro, explique em linguagem simples e sugira tentar de novo.

Exemplos

Pergunta: "Quantos produtos têm cadastrados?"
Dados: {{ "total": 245 }}
Resposta: "Atualmente existem 245 produtos cadastrados."

Pergunta: "Produtos da categoria eletrônicos"
Dados: lista com 15 produtos
Resposta: "Encontrei 15 produtos na categoria eletrônicos. Exemplos: notebook Dell, mouse sem fio e teclado mecânico. Os preços variam de R$ 25,90 a R$ 2.450,00."

Pergunta: "Dados do produto código 123"
Dados: {{ "missing_info": "código do produto" }}
Resposta: "Preciso que você informe o código do produto para poder consultar os dados."

Dados: {{ "error": "authentication_error" }}
Resposta: "Não consegui acessar os dados agora por um problema de autenticação. Tente novamente em alguns minutos."
## O Que Não Fazer
- Não use formatação markdown (*, **, #, etc.)
- Não inclua códigos JSON na resposta final
- Não use termos técnicos desnecessários
- Não seja prolixo ou exagerado
- Não inclua barras invertidas ou aspas extras
- Não copie estruturas JSON literalmente

## Formato da Resposta
Sempre retorne apenas o texto formatado, limpo e humanizado, sem qualquer estrutura JSON ou formatação especial.

Aqui está o que o usuário perguntou:
{question}

Aqui está a resposta do sistema:
{response_json}

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
    prompt = PromptTemplate(
        template=template,
        input_variables=["question", "response_json"]
    )

    access_token = get_token()
    # Valida rota com agente anterior
    route = filter_validator(question)
    validation = route.strip("```json").strip("```").strip()
    route_validation = json.loads(validation)




    if route_validation["validated"] is not True:
        response = {
            "erro": "Rota não validada",
            "detalhes": route_validation
        }

    else:
        if route_validation["method"] != "GET":
            method = route_validation["route"]["method"]
            response = {
                "erro": "Método não suportado",
                "metodo": method
            }
        else:
            response = requests.get(url=route_validation["full_url"], headers={"Authorization": f"Bearer {access_token}"})
            response = response.json()




    prompt_format = prompt.format(question=question, response_json=response)
    response_format = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response_format.content


resposta = route_executor(question='me traga todos os produtos da categoria 1')
print(resposta)