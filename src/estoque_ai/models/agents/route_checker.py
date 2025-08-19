from aiohttp.abc import HTTPException
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from models import llm_gemini
from doc_router import doc_mapper

template = """
Você é um agente especialista em APIs REST. Sua função é analisar a pergunta do usuário e a documentação OpenAPI fornecida para identificar a rota e endpoint corretos para atender à solicitação.

## Sua Responsabilidade
Analisar a pergunta do usuário, consultar a documentação OpenAPI e retornar as informações detalhadas da rota selecionada em formato JSON estruturado.

## Inputs Recebidos
- **question**: Pergunta/solicitação do usuário (string)
- **openapi**: Documentação OpenAPI do arquivo selecionado (JSON/YAML)

## Rotas Principais Disponíveis no eGestor
- Dados da empresa (`/empresa`)
- Contatos (`/contatos`)
- Categoria de produtos (`/categorias`)
- Produtos (`/produtos`)
- Ajuste de estoque (`/ajuste-de-estoque`)
- Serviços (`/servicos`)
- Disponíveis (`/disponiveis`)
- Formas de pagamento (`/formas-de-pagamento`)
- Plano de contas (`/plano-de-contas`)
- Grupo de tributos (`/grupo-de-tributos`)
- Recebimentos (`/recebimentos`)
- Pagamentos (`/pagamentos`)
- Compras (`/compras`)
- Vendas/Ordens de serviço (`/vendas`)
- Devolução de vendas (`/devolucoes`)
- Boletos (`/boletos`)
- Relatórios (`/relatorios`)
- NFSe (`/nfse`)
- NFe (`/nfe`)
- Disco virtual (`/disco-virtual`)
- Usuários (`/usuarios`)

## Instruções de Processamento

1. **Identifique a entidade principal** mencionada na pergunta (ex.: produto, categoria, cliente, pagamento, etc.).
2. **Determine a intenção principal** (listar, consultar, criar, atualizar, excluir, etc.).
3. **Quando a frase mencionar mais de uma entidade**, selecione a rota mais relevante para o núcleo da solicitação, mesmo que outras sejam citadas.
    - Exemplo: "Me traga todos os produtos da categoria Matéria-Prima" → foco: `categoria` (rota `/categorias/{{id}}/produtos`), não `/produtos`.
    - Exemplo: "Listar clientes e seus pedidos" → foco: `clientes` com sub-rota ou parâmetro para pedidos.
4. **Consulte a documentação OpenAPI** para confirmar o endpoint mais adequado (path + method).
5. **Extraia apenas parâmetros não-body**: query, path, header, cookie.
6. **Ignore parâmetros do body** (request body).
7. **Estruture a resposta** conforme o formato especificado.

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

Regras Importantes
Parâmetros

INCLUA APENAS: query, path, header, cookie

EXCLUA SEMPRE: body parameters, request body

INCLUA APENAS parâmetros obrigatórios (required=true)

Liste todos os parâmetros não-body disponíveis na rota selecionada

Mantenha informações de required, type e description da documentação

Autenticação

Sempre inclua o authentication_flow padrão do eGestor

auth_url: sempre "https://api.egestor.com.br/api/oauth/access_token"

base_url: sempre "https://v4.egestor.com.br/api/v1"

expires_in: sempre 900 (15 minutos)

Seleção de Rota

Priorize sempre rotas de listagem/consulta (GET) quando não especificado.

Quando a pergunta envolver relacionamento entre entidades, selecione a rota que representa a entidade principal e utilize sub-rotas ou parâmetros para as secundárias.

Evite selecionar rotas por simples presença de palavras; baseie-se no sentido da solicitação.

Se a pergunta for sobre uma categoria e seus produtos, use /categorias/{{id}}/produtos ou rota equivalente, e não /produtos.

Casos de Erro

Se não encontrar rota adequada na documentação:

```json
{{
  "validated": false,
  "error": "Não foi possível encontrar uma rota adequada para esta solicitação na documentação fornecida"
}}
```

Observações importantes

Em oneOf/anyOf, preencha alternatives como um array de objetos, cada qual com seu requiredFields e bodyFields.

Para allOf, faça o merge e reporte apenas um conjunto final de requiredFields/bodyFields.

Se o contentType principal não for application/json, preencha contentType com o realmente usado (ex.: multipart/form-data) e siga a mesma lógica.

Comportamento

Seja preciso na análise da documentação OpenAPI.

Extraia informações completas e corretas dos parâmetros.

Mantenha consistência no formato de resposta.

Priorize a rota mais específica e semântica para a solicitação do usuário.

Retorne sempre JSON válido e bem estruturado.

Pergunta do usuário:
{question}

Documentação Openapi:
{openapi}

Responda somente com o JSON no formato acima. Não adicione explicações, comentários ou texto extra.
"""

template2 ="""
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
        template=template2,
        input_variables=["question","openapi"]
    )

    doc = doc_mapper(question)

    if doc == 'produtos':
        with open('openapi.json', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'empresa':
        with open('empresa.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'recebimentos':
        with open('recebimentos.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'vendas':
        with open('vendas.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    elif doc == 'outros':
        with open('outros.apib', 'r', encoding='utf-8') as file:
            openapi = file.read()

    else:
        return HTTPException.status_code()

    prompt_format = prompt.format(question=question, openapi=openapi)
    resposta = llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return resposta.content
