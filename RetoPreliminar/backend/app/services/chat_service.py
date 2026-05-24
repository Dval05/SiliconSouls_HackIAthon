# app/services/chat_service.py

import re
import time

from google.genai import types

from app.core.config import (
    GEMINI_MODEL,
    GEMINI_FALLBACK_MODEL,
    GEMINI_FALLBACK_MODELS,
    genai_client,
    supabase,
)
from app.utils.prompts import SYSTEM_PROMPT

_CACHE_TTL_SECONDS = 300
_response_cache = {}

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
                resultados.append(f"Hospital: {nombre} | Copago: ${copago}")
                
        if not resultados:
            return "No se pudieron resolver los nombres de los hospitales."

        # Se retorna el texto a Gemini para que lo interprete y genere su respuesta
        return " | ".join(resultados)
        
    except Exception as e:
        return f"Error consultando la base de datos: {str(e)}"

def buscar_contacto_hospital(nombre_hospital: str) -> str:
    """
    Busca el telefono de un hospital por nombre.
    """
    try:
        res = supabase.table("hospitales").select("nombre_hospital, telefono_hospital").ilike(
            "nombre_hospital", f"%{nombre_hospital}%"
        ).eq("estado_hospital", "01").limit(1).execute()
        if not res.data:
            return f"No se encontro el hospital '{nombre_hospital}'."
        nombre = res.data[0]["nombre_hospital"]
        telefono = res.data[0]["telefono_hospital"]
        return f"Contacto de {nombre}: {telefono}"
    except Exception as e:
        return f"Error consultando el hospital: {str(e)}"

def procesar_mensaje(mensaje_usuario: str, id_plan: str):
    try:
        cache_key = _cache_key(mensaje_usuario, id_plan)
        cached = _cache_get(cache_key)
        if cached:
            return cached

        plan_nombre = id_plan
        plan_res = supabase.table("planes_seguro").select("nombre_plan").eq(
            "id_plan", id_plan
        ).eq("estado_plan", "01").limit(1).execute()
        if plan_res.data:
            plan_nombre = plan_res.data[0]["nombre_plan"]

        # Enviar mensaje inyectando el ID y nombre del plan de forma invisible
        prompt_enriquecido = (
            f"[id_plan: {id_plan}] [nombre_plan: {plan_nombre}] El paciente dice: {mensaje_usuario}"
        )

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[buscar_coberturas_bd, buscar_contacto_hospital],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
        )

        modelos = _lista_modelos()

        last_error = None
        for idx, modelo in enumerate(modelos):
            for intento in range(2):
                try:
                    respuesta = genai_client.models.generate_content(
                        model=modelo,
                        contents=prompt_enriquecido,
                        config=config,
                    )
                    respuesta_texto = respuesta.text or "No pude generar una respuesta en este momento."
                    _cache_set(cache_key, respuesta_texto)
                    return respuesta_texto
                except Exception as inner_error:
                    detalle_error = str(inner_error)
                    last_error = detalle_error
                    if "RESOURCE_EXHAUSTED" in detalle_error or "429" in detalle_error:
                        # Si hay modelo alterno, cambiamos sin esperar.
                        if intento == 0 and idx < len(modelos) - 1:
                            break
                        espera = 45
                        match = re.search(
                            r"retry(?:\s+in|Delay\D+)\s*([0-9]+)",
                            detalle_error,
                            re.IGNORECASE,
                        )
                        if match:
                            espera = min(90, int(match.group(1)))
                        time.sleep(espera)
                        continue
                    raise

        if _es_cuota_agotada(last_error):
            respuesta_texto = _procesar_sin_ai(mensaje_usuario, id_plan, plan_nombre)
            _cache_set(cache_key, respuesta_texto)
            return respuesta_texto

        if _error_sin_tools(last_error):
            respuesta_texto = _procesar_sin_tools(mensaje_usuario, id_plan, plan_nombre)
            _cache_set(cache_key, respuesta_texto)
            return respuesta_texto

        return f"Error al procesar tu consulta: {last_error}"
    except Exception as e:
        detalle_error = str(e)
        if _es_cuota_agotada(detalle_error):
            respuesta_texto = _procesar_sin_ai(mensaje_usuario, id_plan, plan_nombre)
            _cache_set(cache_key, respuesta_texto)
            return respuesta_texto
        if _error_sin_tools(detalle_error):
            respuesta_texto = _procesar_sin_tools(mensaje_usuario, id_plan, plan_nombre)
            _cache_set(cache_key, respuesta_texto)
            return respuesta_texto
        if "RESOURCE_EXHAUSTED" in detalle_error or "429" in detalle_error:
            return (
                "El servicio de IA supero el limite temporal de uso. "
                "Espera un momento e intenta de nuevo."
            )
        return f"Error al procesar tu consulta: {detalle_error}"


def _error_sin_tools(detalle_error: str) -> bool:
    if not detalle_error:
        return False
    return (
        "Unknown name \"systemInstruction\"" in detalle_error
        or "Unknown name \"tools\"" in detalle_error
        or "Unknown name \"toolConfig\"" in detalle_error
    )


def _es_cuota_agotada(detalle_error: str) -> bool:
    if not detalle_error:
        return False
    return "RESOURCE_EXHAUSTED" in detalle_error or "429" in detalle_error


def _extraer_especialidad(mensaje_usuario: str) -> str:
    prompt = (
        "Devuelve SOLO el nombre de la especialidad medica mas adecuada, "
        "en una sola linea, sin explicaciones. Mensaje: "
        f"{mensaje_usuario}"
    )
    texto = _generar_texto_simple(prompt)
    return _limpiar_especialidad(texto)


def _extraer_hospital(mensaje_usuario: str) -> str:
    prompt = (
        "Devuelve SOLO el nombre del hospital mencionado. "
        "Si no hay hospital, responde exactamente: NONE. Mensaje: "
        f"{mensaje_usuario}"
    )
    texto = _generar_texto_simple(prompt)
    if texto.upper() == "NONE" or not texto:
        return ""
    return texto


def _limpiar_especialidad(texto: str) -> str:
    if not texto:
        return ""
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    filtradas = [linea for linea in lineas if not linea.lower().startswith("think:")]
    candidato = filtradas[-1] if filtradas else ""
    if ":" in candidato:
        candidato = candidato.rsplit(":", 1)[-1].strip()
    match = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ ]{3,}", candidato)
    if match:
        return match[-1].strip()
    return candidato.strip()


def _generar_texto_simple(prompt: str) -> str:
    modelos = _lista_modelos()

    last_error = None
    for idx, modelo in enumerate(modelos):
        for intento in range(2):
            try:
                respuesta = genai_client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                )
                return (respuesta.text or "").strip()
            except Exception as inner_error:
                detalle_error = str(inner_error)
                last_error = detalle_error
                if "RESOURCE_EXHAUSTED" in detalle_error or "429" in detalle_error:
                    if intento == 0 and idx < len(modelos) - 1:
                        break
                    espera = 30
                    match = re.search(
                        r"retry(?:\s+in|Delay\D+)\s*([0-9]+)",
                        detalle_error,
                        re.IGNORECASE,
                    )
                    if match:
                        espera = min(90, int(match.group(1)))
                    time.sleep(espera)
                    continue
                raise

    raise RuntimeError(last_error or "Error desconocido al generar contenido")


def _lista_modelos() -> list[str]:
    modelos = [GEMINI_MODEL]
    if GEMINI_FALLBACK_MODEL and GEMINI_FALLBACK_MODEL != GEMINI_MODEL:
        modelos.append(GEMINI_FALLBACK_MODEL)
    for modelo in GEMINI_FALLBACK_MODELS:
        if modelo and modelo not in modelos:
            modelos.append(modelo)
    return modelos


def _cache_key(mensaje_usuario: str, id_plan: str) -> str:
    limpio = " ".join(mensaje_usuario.strip().lower().split())
    return f"{id_plan}::{limpio}"


def _cache_get(key: str) -> str | None:
    item = _response_cache.get(key)
    if not item:
        return None
    timestamp, value = item
    if time.time() - timestamp > _CACHE_TTL_SECONDS:
        _response_cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: str) -> None:
    _response_cache[key] = (time.time(), value)


def _es_consulta_medica(mensaje_usuario: str) -> bool:
    prompt = (
        "Responde SOLO SI o NO. El mensaje esta relacionado con salud, sintomas, "
        "especialidades medicas, hospitales, copagos o seguros de salud? Mensaje: "
        f"{mensaje_usuario}"
    )
    texto = _generar_texto_simple(prompt).strip().upper()
    return texto.startswith("SI")


def _procesar_sin_tools(mensaje_usuario: str, id_plan: str, plan_nombre: str) -> str:
    try:
        if not _es_consulta_medica(mensaje_usuario):
            return (
                "Lo siento, ese tema no esta dentro de mi conocimiento. "
                "Puedo ayudarte con dudas medicas, sintomas, especialidades y copagos."
            )

        if re.search(r"contacto|telefono|tel[eé]fono|llamar|numero", mensaje_usuario, re.IGNORECASE):
            hospital = _extraer_hospital(mensaje_usuario)
            if not hospital:
                return "No encontre el hospital. Indica el nombre exacto para darte el contacto."
            return buscar_contacto_hospital(hospital)

        especialidad = _extraer_especialidad(mensaje_usuario)
        if not especialidad:
            return "No pude identificar la especialidad. Puedes describir los sintomas con mas detalle?"

        resultados = buscar_coberturas_bd(especialidad, id_plan)
        if resultados.startswith("No se encontró la especialidad"):
            return (
                "Lo siento, ese tema no esta dentro de mi conocimiento. "
                "Puedo ayudarte con dudas médicas, síntomas , especialidades, seguros y copagos."
            )
        if resultados.startswith("No se") or resultados.startswith("El plan") or resultados.startswith("Error"):
            return resultados
        return _formatear_respuesta_opciones(especialidad, resultados, plan_nombre)
    except Exception as e:
        return f"Error al procesar tu consulta: {str(e)}"


def _procesar_sin_ai(mensaje_usuario: str, id_plan: str, plan_nombre: str) -> str:
    if re.search(r"contacto|telefono|tel[eé]fono|llamar|numero", mensaje_usuario, re.IGNORECASE):
        match = re.search(r"(?:contacto|telefono|tel[eé]fono|llamar|numero)\s*(?:de)?\s*(.+)", mensaje_usuario, re.IGNORECASE)
        hospital = match.group(1).strip(" .,") if match else ""
        if not hospital:
            return "Indica el nombre exacto del hospital para darte el contacto."
        return buscar_contacto_hospital(hospital)

    match = re.search(r"especialidad\s*(?:de)?\s*([A-Za-zÁÉÍÓÚÑáéíóúñ ]{3,})", mensaje_usuario, re.IGNORECASE)
    if not match:
        return (
            "El servicio de IA esta temporalmente sin cuota. "
            "Indica la especialidad que buscas, por ejemplo: 'especialidad gastroenterologia'."
        )

    especialidad = match.group(1).strip()
    resultados = buscar_coberturas_bd(especialidad, id_plan)
    if resultados.startswith("No se") or resultados.startswith("El plan") or resultados.startswith("Error"):
        return resultados

    return _formatear_respuesta_opciones(especialidad, resultados, plan_nombre)


def _formatear_respuesta_opciones(especialidad: str, resultados: str, plan_nombre: str) -> str:
    opciones = re.findall(
        r"Hospital:\s*(.*?)\s*\|\s*Copago:\s*\$?([0-9]+(?:\.[0-9]+)?)",
        resultados,
    )
    if not opciones:
        return resultados

    mejor_hospital, mejor_copago = min(opciones, key=lambda item: float(item[1]))
    lineas_opciones = "\n\n".join(
        f"Hospital: {nombre} | Copago: ${copago}" for nombre, copago in opciones
    )

    return (
        "Lamento mucho que te sientas mal. El dolor en esa zona suele ser evaluado por la "
        f"especialidad de **{especialidad}**.\n\n"
        f"Para tu plan **{plan_nombre}**, estas son las opciones disponibles con sus copagos:\n\n"
        f"\n {lineas_opciones}\n\n"
        f"La opcion mas económica es **{mejor_hospital}** con copago **${mejor_copago}**."
    )