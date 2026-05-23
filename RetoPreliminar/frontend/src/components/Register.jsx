import { useState, useEffect } from 'react';

export default function Register({ onToggleView }) {
  const [formData, setFormData] = useState({
    cedula: '',
    password: '',
    nombres: '',
    apellidos: '',
    fecha_nacimiento: '',
    id_plan: '' 
  });
  
  const [planes, setPlanes] = useState([]); // Estado para guardar la lista de planes
  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [loading, setLoading] = useState(false);

  // Ejecutar al cargar el componente
  useEffect(() => {
    const fetchPlanes = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/auth/planes');
        if (response.ok) {
          const data = await response.json();
          setPlanes(data);
          // Si hay planes, seleccionamos el primero por defecto para que no se envíe vacío
          if (data.length > 0) {
            setFormData(prev => ({ ...prev, id_plan: data[0].id_plan }));
          }
        }
      } catch (error) {
        console.error("Error al cargar los planes:", error);
      }
    };

    fetchPlanes();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setMensaje({ texto: 'Registro exitoso. Ya puedes iniciar sesión.', tipo: 'success' });
        // Opcional: regresar al login automáticamente después de 2 segundos
        setTimeout(() => onToggleView('login'), 2000);
      } else {
        setMensaje({ texto: data.detail || data.mensaje || 'Error al registrar', tipo: 'error' });
      }
    } catch (err) {
      setMensaje({ texto: 'Error al conectar con el servidor.', tipo: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto bg-white p-8 rounded-xl shadow-lg mt-6">
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Crear Cuenta</h2>
      
      {mensaje.texto && (
        <div className={`p-3 rounded mb-4 text-sm text-center ${mensaje.tipo === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
          {mensaje.texto}
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombres</label>
            <input type="text" name="nombres" value={formData.nombres} onChange={handleChange} required
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Apellidos</label>
            <input type="text" name="apellidos" value={formData.apellidos} onChange={handleChange} required
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cédula</label>
          <input type="text" name="cedula" value={formData.cedula} onChange={handleChange} required
            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
          <input type="password" name="password" value={formData.password} onChange={handleChange} required
            className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Fec. Nacimiento</label>
            <input type="date" name="fecha_nacimiento" value={formData.fecha_nacimiento} onChange={handleChange} required
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Plan de Seguro</label>
            <select 
              name="id_plan" 
              value={formData.id_plan} 
              onChange={handleChange} 
              required
              className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none text-sm bg-white"
            >
              {planes.map((plan) => (
                <option key={plan.id_plan} value={plan.id_plan}>
                  {plan.nombre_plan}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button type="submit" disabled={loading || planes.length === 0}
          className="w-full bg-green-600 text-white font-bold py-3 rounded-lg hover:bg-green-700 transition disabled:bg-green-400 mt-2">
          {loading ? 'Registrando...' : 'Registrarse'}
        </button>
      </form>

      <div className="mt-4 text-center">
        <button onClick={() => onToggleView('login')} type="button" className="text-sm text-blue-600 hover:underline">
          ¿Ya tienes cuenta? Inicia sesión
        </button>
      </div>
    </div>
  );
}