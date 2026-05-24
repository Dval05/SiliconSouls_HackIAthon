import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

export default function Chat({ idPlan, onActivity, onAgentBusy }) {
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const sugerencias = [
    'Tengo un golpe en el brazo y me duele bastante.',
    'Me duele el estómago y me siento muy mal.',
    'Siento mareo y dolor de cabeza desde ayer.'
  ];
  const [mensajes, setMensajes] = useState([
    { rol: 'bot', texto: 'Hola. Cuéntame, ¿qué síntomas tienes o qué especialidad buscas?' }
  ]);
  const [input, setInput] = useState('');
  const [cargando, setCargando] = useState(false);
  const [opcionesClinicas, setOpcionesClinicas] = useState([]);
  const messagesEndRef = useRef(null);

  // Auto-scroll al último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => {
    scrollToBottom();
  }, [mensajes]);

  const extraerOpcionesClinicas = (texto) => {
    const regex = /Hospital:\s*(.*?)\s*\|\s*Copago:\s*\$?([0-9.,]+)/g;
    const opciones = [];
    let match;
    while ((match = regex.exec(texto)) !== null) {
      opciones.push({
        nombre: match[1].trim(),
        copago: match[2].trim()
      });
    }
    return opciones;
  };

  const enviarTexto = async (texto) => {
    if (!texto.trim()) return;
    const mensajeUsuario = texto;
    onActivity?.();
    // Agregar el mensaje del usuario a la pantalla
    setMensajes(prev => [...prev, { rol: 'user', texto: mensajeUsuario }]);
    setInput('');
    setOpcionesClinicas([]);
    setCargando(true);
    onAgentBusy?.(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mensaje: mensajeUsuario, 
          id_plan: idPlan 
        })
      });

      const data = await response.json();
      
      const opciones = extraerOpcionesClinicas(data.respuesta || '');
      // Agregar la respuesta del bot
      setMensajes(prev => [...prev, { rol: 'bot', texto: data.respuesta }]);
      setOpcionesClinicas(opciones);
    } catch (err) {
      setMensajes(prev => [...prev, { rol: 'bot', texto: 'Hubo un error de conexión con el agente médico.' }]);
    } finally {
      setCargando(false);
      onAgentBusy?.(false);
    }
  };

  const manejarSeleccionClinica = (opcion) => {
    onActivity?.();
    enviarTexto(`Quiero el contacto de ${opcion.nombre}.`);
  };

  const enviarMensaje = (e) => {
    e.preventDefault();
    enviarTexto(input);
  };

  return (
    <div className="flex flex-col bg-white rounded-xl shadow-lg h-[80vh] w-full max-w-3xl mx-auto overflow-hidden mt-6">
      
      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
        {mensajes.map((msg, index) => (
          <div key={index} className={`flex ${msg.rol === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] p-4 rounded-2xl ${
              msg.rol === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-white text-gray-800 border border-gray-200 shadow-sm rounded-bl-none'
            }`}>
              <div className="markdown-body">
                <ReactMarkdown>{msg.texto}</ReactMarkdown>
              </div>
            </div>
          </div>
        ))}
        {cargando && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-500 p-3 rounded-2xl rounded-bl-none animate-pulse">
              El agente está escribiendo...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {mensajes.length === 1 && !cargando && (
        <div className="px-4 pb-3 bg-slate-50 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {sugerencias.map((texto) => (
              <button
                key={texto}
                type="button"
                onClick={() => {
                  onActivity?.();
                  setInput(texto);
                }}
                className="text-sm bg-white border border-gray-200 text-gray-700 px-3 py-2 rounded-full hover:border-blue-400 hover:text-blue-700 transition"
              >
                {texto}
              </button>
            ))}
          </div>
        </div>
      )}

      {opcionesClinicas.length > 0 && (
        <div className="px-4 pb-3 bg-slate-50 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {opcionesClinicas.map((opcion) => (
              <button
                key={`${opcion.nombre}-${opcion.copago}`}
                type="button"
                onClick={() => manejarSeleccionClinica(opcion)}
                className="text-sm bg-white border border-gray-200 text-gray-700 px-3 py-2 rounded-full hover:border-blue-400 hover:text-blue-700 transition"
              >
                {opcion.nombre}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input de chat */}
      <form onSubmit={enviarMensaje} className="p-4 bg-white border-t border-gray-200 flex gap-2">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-full px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          placeholder="Escribe tus síntomas aquí..."
          value={input}
          onChange={(e) => {
            onActivity?.();
            setInput(e.target.value);
          }}
          disabled={cargando}
        />
        <button
          type="submit"
          disabled={cargando || !input.trim()}
          className="bg-blue-600 text-white rounded-full px-6 py-2 font-semibold hover:bg-blue-700 transition disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  );
}