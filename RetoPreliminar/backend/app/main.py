from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import auth_controller, chat_controller

app = FastAPI(title="API Estimador Médico")

# Configuración CORS (Permite que React se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar a la URL de tu Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar las rutas
app.include_router(auth_controller.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(chat_controller.router, prefix="/api", tags=["Chat Médico"])

@app.get("/")
def read_root():
    return {"mensaje": "Servidor Backend del Estimador Médico Activo"}