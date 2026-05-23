# app/services/chat_service.py

from app.core.config import GEMINI_MODEL, genai_client, supabase
from app.utils.prompts import SYSTEM_PROMPT

# 1. Definir la herramienta (Tool) que Gemini usará
def buscar_coberturas_bd(nombre_especialidad: str, id_plan: str) -> str:
    """
    Busca en la base de datos los hospitales que ofrecen una especialidad y devuelve el copago para el paciente.
    """
    try:
        # PASO 1: Buscar el ID de la especialidad requerida
        esp_res = supabase.table("especialidades").select("id_especialidad").ilike(
            "nombre_especialidad", f"%{nombre_especialidad}%"
        ).eq("estado_especialidad", "01").execute()
        
        if not esp_res.data:
            return f"No se encontró la especialidad '{nombre_especialidad}' activa en nuestra red."
            
        id_esp = esp_res.data[0]["id_especialidad"]
        
        # PASO 2: Buscar en tarifarios qué hospitales ofrecen esta especialidad
        tarif_res = supabase.table("tarifarios").select("id_hospitales").eq(
            "id_especialidad", id_esp
        ).eq("estado_tarifarios", "01").execute()
        
        if not tarif_res.data:
            return f"Actualmente no hay hospitales registrados con la especialidad '{nombre_especialidad}'."
            
        # Extraemos la lista de IDs de hospitales que sí la ofrecen
        hospitales_con_especialidad = [t["id_hospitales"] for t in tarif_res.data]
        
        # PASO 3: Buscar las coberturas del paciente SOLO en esos hospitales
        coberturas = supabase.table("coberturas").select("id_hospitales, copago_fijo_cobertura").eq(
            "id_plan", id_plan
        ).in_(
            "id_hospitales", hospitales_con_especialidad
        ).eq("estado_cobertura", "01").execute()
        
        if not coberturas.data:
            return f"El plan del paciente no tiene cobertura para la especialidad '{nombre_especialidad}' en los hospitales disponibles."
            
        # PASO 4: Obtener el nombre de cada hospital y formatear los resultados
        resultados = []
        for cob in coberturas.data:
            hosp = supabase.table("hospitales").select("nombre_hospital").eq(
                "id_hospitales", cob["id_hospitales"]
            ).eq("estado_hospital", "01").execute()
            
            if hosp.data:
                nombre = hosp.data[0]["nombre_hospital"]
                copago = cob["copago_fijo_cobertura"]
                resultados.append(f"Hospital: {nombre} - Copago: ${copago}")
                
        if not resultados:
            return "No se pudieron resolver los nombres de los hospitales."

        # Se retorna el texto a Gemini para que lo interprete y genere su respuesta
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