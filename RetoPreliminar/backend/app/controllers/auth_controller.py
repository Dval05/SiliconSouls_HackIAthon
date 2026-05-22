from fastapi import APIRouter, HTTPException
from app.models.schemas import LoginRequest, LoginResponse
from app.services.auth_service import verificar_credenciales

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    resultado = verificar_credenciales(request.cedula, request.password)
    
    if not resultado["success"]:
        raise HTTPException(status_code=401, detail=resultado["mensaje"])
        
    return LoginResponse(
        success=True,
        mensaje=resultado["mensaje"],
        id_plan=resultado["id_plan"],
        nombres=resultado["nombres"]
    )