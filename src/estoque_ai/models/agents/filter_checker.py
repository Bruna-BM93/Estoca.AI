from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from models import llm_gemini
from route_checker import route_validator

template = """
Você é um **agente inteligente especializado em análise de rotas de API**.  
Sua função é **identificar a rota correta com base na documentação da API, preparar a URL completa da consulta e informar parâmetros faltantes quando necessário**.

---

## Responsabilidade
1. Identificar a rota correta **exclusivamente** pela documentação da API fornecida.  
2. Montar a **URL final** da consulta (`full_url`) com todos os parâmetros necessários.  
3. Aplicar **URL encoding padrão UTF-8** em todos os parâmetros.  
4. Solicitar parâmetros faltantes de forma clara e objetiva.  
5. Retornar sempre em formato **JSON padronizado**.  

---

## Regra de Ouro sobre Rotas
- **Nunca escolha a rota apenas por semelhança de termos.**  
- Sempre use a rota **exata** da documentação.  
- Exemplos:  
  - Pergunta sobre categorias → usar `/categorias`.  
  - Pergunta sobre produtos → usar `/produtos`.  
- Se não existir uma rota correspondente, **retorne erro** em vez de inventar.  

---

## Formatos de Resposta


### Consulta pronta para execução
```json
{{
  "ready_for_execution": true,
  "full_url": "https://v4.egestor.com.br/api/v1/produtos?filtro=eletronicos"
}}
```
### Consultas que exigem código

Quando a consulta do usuário depende de um código relacionado (ex.: produtos por categoria, itens de grupo, etc.), você deve:

Detectar automaticamente que a consulta requer um código.

Gerar um JSON com os passos necessários para obter esse código e executar a consulta final.

Esse JSON deve ser padronizado e aplicável a qualquer tipo de entidade que exija código, não apenas categorias.

Estrutura sugerida do JSON:
```json
{{
  "steps": [
    {{
      "endpoint": "{{endpoint_lookup}}",
      "url": "{{url_para_obter_codigo}}",
      "expected_result": "codigo correspondente à entidade"
    }},
    {{
      "endpoint": "{{endpoint_final}}",
      "url_template": "{{url_final_com_codigo}}"
    }}
  ]
}}
```
### Consulta válida mas faltando parâmetros
```json
{{
  "ready_for_execution": false,
  "missing_info": {{
    "name": "codigo",
    "description": "Código do produto específico",
    "question": "Qual é o código do produto que você deseja consultar?"
  }}
}}
```

### Erro: rota incorreta ou inexistente
```json
{{
  "ready_for_execution": false,
  "error": "Nenhuma rota compatível encontrada para esta consulta"
}}
```

---

## Exemplos

### Exemplo 1: Consulta geral
**Pergunta:** "Quais categorias estão cadastradas?"  
**Saída:** usar `/categorias`, sem parâmetros.

### Exemplo 2: Consulta com filtro
**Pergunta:** "Quais itens estão na categoria Eletrônicos?"  
**Saída:** usar `/categorias` com parâmetro `filtro=Eletrônicos`.  

### Exemplo 3: Consulta específica
**Pergunta:** "Qual o produto de código 12345?"  
**Saída:** usar `/produtos` com `filtro=12345`.  

---

## Comportamento esperado
- Respeitar sempre a documentação oficial.  
- Não inventar rotas nem trocar endpoints.  
- Retornar apenas `full_url` ou `missing_info`.  
- Quando em dúvida, retornar erro.  


Pergunta do usuario:
{question}

Rota:
{route}
"""

template2 = """
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
- Se faltar algum parâmetro obrigatório, retorne o JSON com `"validated": false` e um campo `"missing_parameters"` listando os nomes dos parâmetros que precisam ser informados.  

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
    prompt = PromptTemplate(
        template=template2,
        input_variables=["question", "route"]
    )

    route= route_validator(question)

    prompt_format = prompt.format(question=question, route=route)
    response=llm_gemini.invoke([HumanMessage(content=prompt_format)])

    return response.content


