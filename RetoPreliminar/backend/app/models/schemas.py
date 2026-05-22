from pydantic import BaseModel

class LoginRequest(BaseModel):
    cedula: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    mensaje: str
    id_plan: str | None = None
    nombres: str | None = None

class ChatRequest(BaseModel):
    mensaje: str
    id_plan: str

class ChatResponse(BaseModel):
    respuesta: str