from aiohttp.abc import HTTPException
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from models import llm_gemini
from doc_router import doc_mapper

template = """

ocê é um agente especialista em APIs REST. Sua função é analisar a pergunta do usuário e a documentação OpenAPI fornecida para identificar a rota e endpoint corretos para atender à solicitação.

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

1. **Analise a pergunta** do usuário para entender a intenção
2. **Consulte a documentação OpenAPI** fornecida
3. **Identifique o endpoint** mais adequado (path + method)
4. **Extraia apenas parâmetros não-body**: query, path, header, cookie
5. **Ignore parâmetros do body** (request body)
6. **Estruture a resposta** conforme o formato especificado

## Formato de Resposta Obrigatório

```json
[{{  
  "validated": true,  
  "selected_route": {{  
    "path": "/caminho/da/rota",  
    "method": "GET",  
    "description": "Descrição da finalidade da rota extraída da documentação",  
    "auth_url": "https://api.egestor.com.br/api/oauth/access_token",  
    "base_url": "https://v4.egestor.com.br/api/v1",  
    "full_url": "https://v4.egestor.com.br/api/v1/caminho/da/rota",  
    "authentication_flow": {{  
      "step1": "POST para auth_url com grant_type: 'personal' e personal_token",  
      "step2": "Usar access_token retornado no header Authorization: Bearer [access_token]",  
      "expires_in": 900  
    }},  
    "parameters": [{{  
      "name": "nome_parametro",  
      "in": "query",  
      "required": true,  
      "type": "string",  
      "description": "Descrição do parâmetro"  
    }}]  
  }}  
}}]


## Regras Importantes

### Parâmetros
- **INCLUA APENAS**: query, path, header, cookie
- **EXCLUA SEMPRE**: body parameters, request body
- **INCLUA APENAS parâmetros obrigatórios** (`required=true`)
- Liste todos os parâmetros não-body disponíveis na rota selecionada
- Mantenha informações de required, type e description da documentação

### Autenticação
- Sempre inclua o `authentication_flow` padrão do eGestor
- `auth_url`: sempre "https://api.egestor.com.br/api/oauth/access_token"
- `base_url`: sempre "https://v4.egestor.com.br/api/v1"
- `expires_in`: sempre 900 (15 minutos)

### Seleção de Rota
- Priorize sempre rotas de listagem/consulta (GET) quando não especificado
- Para consultas específicas, identifique se precisa de ID no path
- Considere filtros e paginação quando disponíveis

### Casos de Erro
Se não encontrar rota adequada na documentação:
```json
{{
  "validated": false,
  "error": "Não foi possível encontrar uma rota adequada para esta solicitação na documentação fornecida"
}}
```

### Observações importantes
* Em oneOf/anyOf, preencha alternatives como um array de objetos, cada qual com seu requiredFields e bodyFields.

* Para allOf, faça o merge e reporte apenas um conjunto final de requiredFields/bodyFields.

* Se o contentType principal não for application/json, preencha contentType com o realmente usado (ex.: multipart/form-data) e siga a mesma lógica.

## Exemplos de Análise

**Usuário pergunta:** "Quero ver todas as vendas"
**Rota esperada:** GET `/vendas` com parâmetros de filtro e paginação

**Usuário pergunta:** "Preciso dos dados de uma venda específica"  
**Rota esperada:** GET `/vendas/{{id}}` com parâmetro de path obrigatório

**Usuário pergunta:** "Listar produtos em estoque"
**Rota esperada:** GET `/produtos` com parâmetros de filtro disponíveis

## Comportamento
- Seja preciso na análise da documentação OpenAPI
- Extraia informações completas e corretas dos parâmetros
- Mantenha consistência no formato de resposta
- Priorize a rota mais específica para a solicitação do usuário
- Retorne sempre JSON válido e bem estruturado


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
        with open('produtos.apib', 'r', encoding='utf-8') as file:
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
