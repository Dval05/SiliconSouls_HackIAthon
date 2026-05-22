from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import procesar_mensaje

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def enviar_mensaje(request: ChatRequest):
    try:
        texto_respuesta = procesar_mensaje(request.mensaje, request.id_plan)
        return ChatResponse(respuesta=texto_respuesta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))