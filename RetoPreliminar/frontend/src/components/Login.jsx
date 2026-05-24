import { useState } from 'react';

export default function Login({ onLoginSuccess, onToggleView }) {
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const [cedula, setCedula] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [cedulaWarning, setCedulaWarning] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (cedula.length !== 10) {
      setError('La cédula debe tener 10 dígitos numéricos.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cedula, password })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        onLoginSuccess({
          id_plan: data.id_plan,
          nombre_plan: data.nombre_plan,
          nombres: data.nombres
        });
      } else {
        setError(data.detail || data.mensaje || 'Credenciales incorrectas');
      }
    } catch (err) {
      setError('Error al conectar con el servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto bg-white p-8 rounded-xl shadow-lg mt-10">
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Iniciar Sesión</h2>
      
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4 text-sm text-center">
          {error}
        </div>
      )}

      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cédula</label>
          <input 
            type="text" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Ej: 1718293045"
            value={cedula}
            onChange={(e) => {
              const raw = e.target.value;
              const numeric = raw.replace(/\D/g, '').slice(0, 10);
              setCedula(numeric);
              setCedulaWarning(raw !== numeric ? 'Solo se permiten números.' : '');
            }}
            required
          />
          {cedulaWarning && (
            <p className="text-xs text-amber-600 mt-1">{cedulaWarning}</p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
          <input 
            type="password" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition disabled:bg-blue-400"
        >
          {loading ? 'Verificando...' : 'Entrar'}
        </button>
      </form>

      <div className="mt-4 text-center">
        <button onClick={() => onToggleView('register')} className="text-sm text-blue-600 hover:underline">
          ¿No tienes cuenta? Regístrate aquí
        </button>
      </div>
    </div>
  );
}