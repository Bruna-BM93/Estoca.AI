from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional
import uuid

from src.estoque_ai.models.agents.response_format import route_executor
from src.estoque_ai.mongodb_database import mongo_client

router = APIRouter(prefix='/chat', tags=['Chat'])


class ChatQuestion(BaseModel):
    mensagem: str
    session: Optional[str] = None


class ChatResponse(BaseModel):
    pergunta: str
    resposta: str
    session: str


@router.post('/', response_model=ChatResponse, status_code=status.HTTP_200_OK, summary='Enviar nova Mensagem de Consulta')
def enviar_mensagem(pergunta: ChatQuestion):
    chat_session = mongo_client['chathistory'].chatSession
    conversation_history = []

    if pergunta.session:
        session = pergunta.session
        conversation_history = list(chat_session.find({'session': session}))

    else:
        session = str(uuid.uuid4())


    resposta = route_executor(pergunta.mensagem, history=conversation_history)

    interation = {
        'pergunta': pergunta.mensagem,
        'resposta': resposta,
        'session': session,
    }

    chat_session.insert_one(interation)

    return interation

