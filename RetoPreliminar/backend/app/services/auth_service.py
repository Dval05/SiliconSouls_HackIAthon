import bcrypt
from app.core.config import supabase

def verificar_credenciales(cedula: str, password_plano: str):
    try:
        # 1. Buscar usuario por cédula
        user_response = supabase.table("usuarios").select("*").eq("cedula_usuarios", cedula).execute()
        
        if not user_response.data:
            return {"success": False, "mensaje": "Usuario no encontrado."}
            
        usuario = user_response.data[0]
        
        # 2. Verificar la contraseña con el Hash de la BD
        hash_bd = usuario["password_hash"].encode('utf-8')
        if not bcrypt.checkpw(password_plano.encode('utf-8'), hash_bd):
            return {"success": False, "mensaje": "Contraseña incorrecta."}
            
        # 3. Si es correcto, buscar los datos del paciente
        id_usuario = usuario["id_usuarios"]
        paciente_response = supabase.table("pacientes").select("id_plan, nombres_pacientes, apellidos_pacientes").eq("id_usuarios", id_usuario).execute()
        
        if not paciente_response.data:
             return {"success": False, "mensaje": "Perfil de paciente no encontrado."}
             
        paciente = paciente_response.data[0]
        
        return {
            "success": True, 
            "mensaje": "Login exitoso", 
            "id_plan": paciente["id_plan"],
            "nombres": f"{paciente['nombres_pacientes']} {paciente['apellidos_pacientes']}"
        }
        
    except Exception as e:
        return {"success": False, "mensaje": f"Error en el servidor: {str(e)}"}

# --- NUEVA FUNCIÓN DE REGISTRO SECUENCIAL ---
def registrar_usuario(datos: dict):
    try:
        # 1. Verificar si la cédula ya existe
        existe = supabase.table("usuarios").select("id_usuarios").eq("cedula_usuarios", datos["cedula"]).execute()
        if existe.data:
            return {"success": False, "mensaje": "La cédula ya está registrada."}

        # 2. Obtener y calcular el siguiente id_usuarios (Formato: U001, U002...)
        res_usuarios = supabase.table("usuarios").select("id_usuarios").order("id_usuarios", desc=True).limit(1).execute()
        if res_usuarios.data:
            ultimo_id_usuario = res_usuarios.data[0]["id_usuarios"]  # ej: "U009"
            siguiente_num_usuario = int(ultimo_id_usuario.replace("U", "")) + 1
        else:
            siguiente_num_usuario = 1
            
        nuevo_id_usuario = f"U{siguiente_num_usuario:03d}" # Rellena con ceros: U010

        # 3. Obtener y calcular el siguiente id_paciente (Formato: PA001, PA002...)
        res_pacientes = supabase.table("pacientes").select("id_paciente").order("id_paciente", desc=True).limit(1).execute()
        if res_pacientes.data:
            ultimo_id_paciente = res_pacientes.data[0]["id_paciente"]  # ej: "PA009"
            siguiente_num_paciente = int(ultimo_id_paciente.replace("PA", "")) + 1
        else:
            siguiente_num_paciente = 1
            
        nuevo_id_paciente = f"PA{siguiente_num_paciente:03d}" # Rellena con ceros: PA010

        # 4. Hashear la contraseña
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(datos["password"].encode('utf-8'), salt).decode('utf-8')

        # 5. Insertar en tabla 'usuarios'
        nuevo_usuario = {
            "id_usuarios": nuevo_id_usuario,
            "cedula_usuarios": datos["cedula"],
            "password_hash": password_hash,
            "estado_usuario": "01"
        }
        supabase.table("usuarios").insert(nuevo_usuario).execute()

        # 6. Insertar en tabla 'pacientes'
        nuevo_paciente = {
            "id_paciente": nuevo_id_paciente,
            "id_usuarios": nuevo_id_usuario,
            "id_plan": datos["id_plan"],
            "nombres_pacientes": datos["nombres"],
            "apellidos_pacientes": datos["apellidos"],
            "fec_nac_paciente": datos["fecha_nacimiento"],
            "estado_paciente": "01"
        }
        supabase.table("pacientes").insert(nuevo_paciente).execute()

        return {"success": True, "mensaje": "Usuario registrado exitosamente."}

    except Exception as e:
        return {"success": False, "mensaje": f"Error al registrar: {str(e)}"}

def obtener_planes_activos():
    try:
        # Traemos solo el ID y el Nombre de los planes cuyo estado sea '01' (activo)
        res = supabase.table("planes_seguro").select("id_plan, nombre_plan").eq("estado_plan", "01").execute()
        return {"success": True, "planes": res.data}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al obtener planes: {str(e)}"}