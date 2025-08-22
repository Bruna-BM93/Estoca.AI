from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

import json

from src.estoque_ai.models.agents.models import llm_gemini

template = """
## Tarefa
Dada a mensagem do usuário, retorne **apenas** o nome do arquivo relevante: `vendas`, `recebimentos`, `produtos`, `empresa` ou `outros`.

## Palavras-chave
- **vendas**: vendas, venda, boleto, boletos, devolução, devoluções, faturamento, nota fiscal, pedido de venda  
- **recebimentos**: recebimentos, recebimento, compras, compra, pagamentos, pagamento, contas a receber, contas a pagar  
- **produtos**: produtos, produto, estoque, categoria, categorias, inventário, item, itens  
- **empresa**: empresa, contatos, contato, fornecedores, fornecedor, transportadores, transportador, clientes, cliente, pessoas  
- **outros**: serviços, serviço, plano de contas, contas contábeis, disponíveis, relatórios gerais  

## Regras
1. Analise palavras-chave na mensagem.  
2. Retorne **somente** o arquivo mais provável.  
3. Em caso de ambiguidade, escolha o mais relevante.  
4. Sem explicações ou informações extras.

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

