from aiohttp.abc import HTTPException
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from src.estoque_ai.models.agents.models import llm_gemini
from src.estoque_ai.models.agents.doc_router import doc_mapper


template ="""
Você é um agente especialista em APIs REST do eGestor. Sua função é receber **uma pergunta do usuário** e a **documentação OpenAPI resumida** e retornar a rota e endpoint corretos em JSON estruturado.

## Regras Principais
1. **Contexto Essencial:** Use apenas as informações necessárias da pergunta e do resumo de documentação. Ignore histórico completo.
2. **Intenção e Entidade:** Identifique:
   - Entidade principal (ex.: produto, categoria, cliente).
   - Intenção (listar, consultar, criar, atualizar, excluir).
   - Se houver múltiplas entidades, selecione a rota da entidade principal e trate as secundárias via parâmetros ou sub-rotas.
3. **Rotas do eGestor:** Use somente rotas disponíveis para consultas/GET quando não especificado.
4. **Parâmetros:** Inclua apenas parâmetros obrigatórios não-body (query, path, header, cookie). Ignore body/request body.
5. **Consulta OpenAPI:** Use o resumo da documentação para confirmar path, method e parâmetros obrigatórios. Use merge de allOf, alternativas de oneOf/anyOf como arrays resumidos.

## Formato de Resposta Obrigatório
```json
[{{  
  "validated": true,  
  "selected_route": {{  
    "path": "/caminho/da/rota",  
    "method": "GET",    
    "full_url": "https://v4.egestor.com.br/api/v1/caminho/da/rota",    
    }},  
    "parameters": [{{  
      "name": "nome_parametro",  
      "in": "query",  
      "required": true,  
      "type": "string",   
    }}]  
  }}  
}}]

Pergunta do usuário:
{question}

Documentação Openapi:
{openapi}

Responda somente com o JSON no formato acima. Não adicione explicações, comentários ou texto extra.

"""
def route_validator(question):
    """
    SEGUNDO AGENTE - SELETOR DE ROTAS ERP

    Função: Analisar a pergunta do usuário e a documentação OpenAPI para identificar
    o endpoint correto e extrair informações detalhadas da rota selecionada.

    Input:
    - question (string): Pergunta/solicitação do usuário
    - openapi (JSON/YAML/apib): Documentação OpenAPI do arquivo correspondente

    Output: JSON com rota selecionada contendo:
    - path, method, description
    - URLs de autenticação e base
    - Fluxo de autenticação OAuth
    - Lista de parâmetros não-body (query, path, header, cookie)

    Regras principais:
    - Lista apenas parâmetros não-body (exclui request body)
    - Prioriza rotas de consulta (GET) quando não especificado
    - Inclui informações de autenticação padrão do eGestor
    - Retorna erro estruturado se não encontrar rota adequada

    Este agente atua como intermediário, transformando a intenção do usuário
    em especificação técnica da API para os agentes subsequentes.
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["question","openapi"]
    )

    doc = doc_mapper(question)

    if doc == 'produtos':
        import os
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'openapi.json')



        with open(file_path, 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'empresa':
        return {"erro":"Sem acesso"}
        with open('src/estoque_ai/models/agents/empresa.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'recebimentos':
        return {"erro":"Sem acesso"}
        with open('src/estoque_ai/models/agents/recebimentos.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'vendas':
        return {"erro":"Sem acesso"}
        with open('src/estoque_ai/models/agents/vendas.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'outros':
        return {"erro":"Sem acesso"}
        with open('src/estoque_ai/models/agents/outros.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    else:
        return {"erro":"Sem acesso"}

    prompt_format = prompt.format(question=question, openapi=openapi)
    resposta = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return resposta.content

