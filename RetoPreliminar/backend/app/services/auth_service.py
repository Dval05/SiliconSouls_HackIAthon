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