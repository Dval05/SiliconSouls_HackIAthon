import logging

from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import procesar_mensaje

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
def enviar_mensaje(request: ChatRequest):
    try:
        texto_respuesta = procesar_mensaje(request.mensaje, request.id_plan)
        return ChatResponse(respuesta=texto_respuesta)
    except Exception as e:
        logger.exception("Error procesando /chat")
        return ChatResponse(respuesta=f"Error al procesar tu consulta: {str(e)}")