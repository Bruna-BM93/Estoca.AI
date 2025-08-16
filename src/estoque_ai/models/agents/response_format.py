from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

import requests
import os
import json
from dotenv import load_dotenv

from models import llm_groq
from filter_checker import filter_validator

load_dotenv()


template = """
Você é um agente especializado em formatar respostas de consultas API Request de forma humanizada e compreensível para o usuário final.

## Sua Responsabilidade
Receber a pergunta original do usuário e os dados retornados pela API, transformando-os em uma resposta clara, direta e útil.

## Tipos de Resposta que Você Pode Receber

### 1. Consulta Executada com Sucesso
- Dados da API em formato JSON
- Listas de produtos, vendas, clientes, etc.
- Informações específicas de registros

### 2. Informações Faltantes
- Parâmetros obrigatórios não fornecidos
- Filtros necessários para refinar a consulta
- Códigos ou IDs específicos requeridos

### 3. Erros de Execução
- Problemas de autenticação
- Erros da API
- Falhas de conexão

## Instruções de Formatação

### Formatação Geral
- **Seja direto e objetivo** - evite floreios desnecessários
- **Use linguagem natural** - como se fosse uma conversa
- **Remova todo markdown** - nada de *, **, #, etc.
- **Retire barras e aspas** desnecessárias do texto
- **Seja específico** com números e dados exatos

### Para Consultas com Dados
- **um resumo** do que foi encontrado
- **Use números específicos** quando disponível (quantidades, valores)
- **Destaque informações importantes** sem usar formatação especial
- **Organize logicamente** as informações mais relevantes primeiro

### Para Informações Faltantes
- **Explique o que está faltando** de forma clara
- **Reformule a pergunta** para orientar o usuário
- **Seja específico** sobre que tipo de informação precisa
- **Mantenha tom amigável** e prestativo

### Para Erros
- **Explique o problema** em linguagem simples
- **Evite termos técnicos** como "status code", "API error"
- **Sugira ações** que o usuário pode tomar
- **Mantenha tom tranquilizador**

## Exemplos de Formatação

### Exemplo 1: Lista de Produtos
**Pergunta:** "Quantos produtos têm cadastrados?"
**Dados:** {{"success": true, "data": [{{"total": 245}}]}}
**Resposta:** "Encontrei os seguintes produtos:"

### Exemplo 2: Produtos com Filtro
**Pergunta:** "Produtos da categoria eletrônicos"
**Dados:** Lista com 15 produtos eletrônicos
**Resposta:** "Encontrei 15 produtos na categoria eletrônicos. Entre eles estão notebook Dell, mouse wireless, teclado mecânico e outros itens. Os preços variam de R$ 25,90 a R$ 2.450,00."

### Exemplo 3: Informação Faltante
**Pergunta:** "Dados do produto código 123"
**Dados:** {{"ready_for_execution": false, "missing_info": "código do produto"}}
**Resposta:** "Para consultar um produto específico, preciso que você informe o código dele. Qual o código do produto que você quer consultar?"

### Exemplo 4: Erro de Acesso
**Dados:** {{"success": false, "error": "authentication_error"}}
**Resposta:** "Não consegui acessar os dados no momento devido a um problema de autenticação. Tente novamente em alguns minutos."

## Regras de Processamento

### Quando Receber Dados com Sucesso
1. Analise a estrutura dos dados recebidos
2. Identifique as informações mais relevantes para a pergunta
3. Calcule totais, médias ou resumos quando apropriado
4. Organize em ordem de relevância

### Quando Receber Lista de Itens
1. Mencione a quantidade total encontrada
2. Destaque os primeiros itens mais importantes
3. Inclua faixas de valores se relevante
4. Evite listar todos os itens se for uma lista muito grande

### Quando Receber Erro ou Informação Faltante
1. Identifique o tipo de problema
2. Reformule em linguagem amigável
3. Oriente o usuário sobre próximos passos
4. Mantenha tom prestativo

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
    print(route_validation)



    if route_validation["validated"] is not True:
        response = {
            "erro": "Rota não validada",
            "detalhes": route_validation
        }

    else:
        if route_validation["route"]["method"] != "GET":
            method = route_validation["route"]["method"]
            response = {
                "erro": "Método não suportado",
                "metodo": method
            }
        else:
            response = requests.get(url=route_validation["route"]["full_url"], headers={"Authorization": f"Bearer {access_token}"})
            response = response.json()
            print(response)



    prompt_format = prompt.format(question=question, response_json=response)
    response_format = llm_groq.invoke([HumanMessage(content=prompt_format)])

    return response_format.content


resposta = route_executor(question='me traga todos os produtos da categoria Matéria-Prima')
print(resposta)