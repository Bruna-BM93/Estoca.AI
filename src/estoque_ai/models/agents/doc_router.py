from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

import json

from models import llm_gemini

template = """
Você é um agente especialista em compreensão de texto. Seu trabalho é analisar a mensagem do usuário e, com base em seu conteúdo, determinar qual arquivo de documentação da API deve ser consultado para responder à solicitação.

## Sua Responsabilidade
Classificar a solicitação do usuário e retornar APENAS o nome do arquivo correspondente.

## Arquivos Disponíveis e Suas Categorias

### 1. **vendas**
- Contém: vendas, boletos, devolução
- Use quando o usuário mencionar: vendas, venda, boleto, boletos, devolução, devoluções, faturamento, nota fiscal, pedido de venda

### 2. **recebimentos** 
- Contém: recebimento, compras, pagamentos
- Use quando o usuário mencionar: recebimentos, recebimento, compras, compra, pagamentos, pagamento, contas a receber, contas a pagar

### 3. **outros**
- Contém: serviços, disponíveis, plano de contas
- Use quando o usuário mencionar: serviços, serviço, plano de contas, contas contábeis, disponíveis, relatórios gerais

### 4. **produtos**
- Contém: categorias, produtos, estoque
- Use quando o usuário mencionar: produtos, produto, estoque, categoria, categorias, inventário, item, itens

### 5. **empresa**
- Contém: empresa, contatos, fornecedores, transportadores, clientes
- Use quando o usuário mencionar: empresa, contatos, contato, fornecedores, fornecedor, transportadores, transportador, clientes, cliente, pessoas

## Instruções de Funcionamento

1. **Analise** a mensagem do usuário
2. **Identifique** palavras-chave relacionadas aos arquivos
3. **Determine** qual arquivo é mais apropriado
4. **Retorne** APENAS o nome do arquivo

## Regras Importantes
- Use apenas os nomes de arquivos: vendas, recebimentos, outros, produtos, empresa
- Se houver ambiguidade, escolha o arquivo mais provável baseado no contexto
- Mantenha consistência nas respostas para solicitações similares

## Comportamento
- Seja preciso e direto
- Não forneça informações além da classificação
- Foque apenas na análise das palavras-chave

Pergunta do usuário:
{question}

Responda somente com o nome do arquivo.
"""
def doc_mapper(question):
    """
    Função: Analisar a mensagem do usuário e determinar qual arquivo de documentação
    da API do eGestor deve ser consultado pelos próximos agentes.

    Input: Mensagem natural do usuário (string)
    Output: nome do arquivo

    Arquivos disponíveis:
    - vendas: vendas, boletos, devolução
    - recebimentos: recebimento, compras, pagamentos
    - outros: serviços, disponíveis, plano de contas
    - produtos: categorias, produtos, estoque
    - empresa: empresa, contatos, fornecedores, transportadores, clientes

    Este agente atua como o primeiro filtro do sistema, direcionando a consulta
    para a documentação correta antes dos agentes de roteamento e validação.
    """
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"]
    )

    prompt_format = prompt.format(question=question)
    response = llm_gemini.invoke([HumanMessage(content=prompt_format)])
    #response = response.content.strip("```json").strip("```").strip()
    #response_json = json.loads(response)

    return response.content

