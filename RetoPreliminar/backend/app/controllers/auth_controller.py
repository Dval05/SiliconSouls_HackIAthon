from fastapi import APIRouter, HTTPException
from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest, StandardResponse
from app.services.auth_service import verificar_credenciales, registrar_usuario, obtener_planes_activos
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
        nombre_plan=resultado.get("nombre_plan"),
        nombres=resultado["nombres"]
    )

# --- NUEVA RUTA DE REGISTRO ---
@router.post("/register", response_model=StandardResponse)
def register(request: RegisterRequest):
    # Convertimos el modelo Pydantic a diccionario
    resultado = registrar_usuario(request.model_dump())
    
    if not resultado["success"]:
        raise HTTPException(status_code=400, detail=resultado["mensaje"])
        
    return StandardResponse(success=True, mensaje=resultado["mensaje"])

# --- NUEVA RUTA PARA LOS PLANES ---
@router.get("/planes")
def get_planes():
    resultado = obtener_planes_activos()
    if not resultado["success"]:
        raise HTTPException(status_code=500, detail=resultado["mensaje"])
    return resultado["planes"] # Devuelve la lista directamente