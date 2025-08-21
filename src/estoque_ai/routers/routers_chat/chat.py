from typing import Optional
import uuid
from fastapi import APIRouter, status
from pydantic import BaseModel
from estoque_ai.models.agents import response_format


router = APIRouter(prefix="/chat", tags=["Chat"])
class ChatQuestion(BaseModel):
    mensagem: str
    session: Optional[str] = None

class ChatResponse(BaseModel):
    pergunta: str
    resposta: str
    session: str

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK, summary="Enviar nova Mensagem de Consulta")
def enviar_mensagem(pergunta: ChatQuestion):
    chat_sessions = mongo_client["chat_estoqueai"].chat_sessions
    conversation_history = []

    if pergunta.session:
        session = pergunta.session
        conversation_history = list(chat_sessions.find({"session": session}))

    else:
        session = str(uuid.uuid4())

        # Inserindo no MongoDB o registro da conversa/interação


    resposta, consulta_sql = response_format(pergunta.mensagem, historico=conversation_history)

    interacao = {
        "pergunta": pergunta.mensagem,
        "resposta": resposta,
        "session": session,
    }

    chat_sessions.insert_one(interacao | {"consulta_sql": consulta_sql})


    return interacao

