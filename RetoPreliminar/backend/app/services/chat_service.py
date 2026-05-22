from app.core.config import GEMINI_MODEL, genai_client, supabase
from app.utils.prompts import SYSTEM_PROMPT

# 1. Definir la herramienta (Tool) que Gemini usará
def buscar_coberturas_bd(nombre_especialidad: str, id_plan: str) -> str:
    """
    Busca en la base de datos los hospitales que ofrecen una especialidad y devuelve el copago para el paciente.
    """
    try:
        # En un escenario real más complejo, aquí haríamos un JOIN o una vista.
        # Por simplicidad, traemos las coberturas del plan y cruzamos en memoria o con RPC.
        # Aquí consultamos las coberturas activas para ese plan
        coberturas = supabase.table("coberturas").select("id_hospitales, copago_fijo_cobertura").eq("id_plan", id_plan).eq("estado_cobertura", "01").execute()
        
        if not coberturas.data:
            return "No hay cobertura en ningún hospital para este plan."
            
        resultados = []
        for cob in coberturas.data:
            hosp = supabase.table("hospitales").select("nombre_hospital").eq("id_hospitales", cob["id_hospitales"]).execute()
            if hosp.data:
                nombre = hosp.data[0]["nombre_hospital"]
                copago = cob["copago_fijo_cobertura"]
                resultados.append(f"Hospital: {nombre} - Copago: ${copago}")
                
        return " | ".join(resultados)
    except Exception as e:
        return f"Error consultando la base de datos: {str(e)}"

def procesar_mensaje(mensaje_usuario: str, id_plan: str):
    # Enviar mensaje inyectando el ID del plan de forma invisible
    prompt_enriquecido = f"[ID_PLAN_ACTUAL: {id_plan}] El paciente dice: {mensaje_usuario}"

    respuesta = genai_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt_enriquecido,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "tools": [buscar_coberturas_bd],
            "tool_config": {"function_calling_config": {"mode": "AUTO"}},
        },
    )
    return respuesta.text