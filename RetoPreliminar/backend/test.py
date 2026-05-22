from app.services.auth_service import verificar_credenciales
from app.services.chat_service import buscar_coberturas_bd, procesar_mensaje

print("==================================================")
print("🚀 INICIANDO PRUEBA DEL ESTIMADOR MÉDICO (TERMINAL)")
print("==================================================\n")

# --- PRUEBA 1: AUTENTICACIÓN ---
print("1️⃣ Probando Login en Supabase...")
# Usamos a Carlos Andrés (Plan Premium)
cedula_prueba = "1718293045" 
password_prueba = "secreto123"

resultado_login = verificar_credenciales(cedula_prueba, password_prueba)

if not resultado_login["success"]:
    print(f"❌ Error en el login: {resultado_login['mensaje']}")
    exit()

id_plan = resultado_login["id_plan"]
nombres = resultado_login["nombres"]
print(f"✅ Login exitoso. Bienvenido {nombres}.")
print(f"📋 Plan detectado: {id_plan}\n")


# --- PRUEBA 2: BÚSQUEDA DIRECTA EN BASE DE DATOS ---
print("2️⃣ Probando la herramienta de búsqueda SQL (Tool)...")
# Simulamos que Gemini decidió buscar "Traumatología y Ortopedia"
resultado_sql = buscar_coberturas_bd("Traumatología y Ortopedia", id_plan)
print(f"🔍 Resultados crudos de la BD: {resultado_sql}\n")


# --- PRUEBA 3: EL AGENTE GEMINI EN ACCIÓN ---
print("3️⃣ Probando la Inteligencia Artificial (Gemini + Supabase)...")
mensaje_paciente = "Me muele el pecho son como punzadas por momentos ¿A dónde puedo ir y cuánto me va a costar?"
print(f"🗣️ Paciente dice: '{mensaje_paciente}'\n")

print("⏳ Gemini está pensando y consultando la base de datos...")
respuesta_final = procesar_mensaje(mensaje_paciente, id_plan)

print("==================================================")
print("🤖 RESPUESTA DEL AGENTE MÉDICO:")
print("==================================================")
print(respuesta_final)
print("==================================================")