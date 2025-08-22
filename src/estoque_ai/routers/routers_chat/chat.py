import json
from typing import Optional
import uuid

from dns.e164 import query
from fastapi import APIRouter, status
from pydantic import BaseModel
from src.estoque_ai.models.agents.response_format import route_executor
from src.estoque_ai.mongodb_database import mongo_client

router = APIRouter(prefix="/chat", tags=["Chat"])
class ChatQuestion(BaseModel):
    mensagem: str
    #session: Optional[str] = None

class ChatResponse(BaseModel):
    pergunta: str
    resposta: str
    #session: str

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK, summary="Enviar nova Mensagem de Consulta")
def enviar_mensagem(pergunta: ChatQuestion):

    resposta = route_executor(pergunta)

    return {
        "pergunta": pergunta.mensagem,
        "resposta": resposta
    }

