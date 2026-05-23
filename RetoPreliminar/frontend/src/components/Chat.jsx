import { useState, useRef, useEffect } from 'react';

export default function Chat({ idPlan }) {
  const [mensajes, setMensajes] = useState([
    { rol: 'bot', texto: 'Hola. Cuéntame, ¿qué síntomas tienes o qué especialidad buscas?' }
  ]);
  const [input, setInput] = useState('');
  const [cargando, setCargando] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll al último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(() => {
    scrollToBottom();
  }, [mensajes]);

  const enviarMensaje = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const mensajeUsuario = input;
    // Agregar el mensaje del usuario a la pantalla
    setMensajes(prev => [...prev, { rol: 'user', texto: mensajeUsuario }]);
    setInput('');
    setCargando(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mensaje: mensajeUsuario, 
          id_plan: idPlan 
        })
      });

      const data = await response.json();
      
      // Agregar la respuesta del bot
      setMensajes(prev => [...prev, { rol: 'bot', texto: data.respuesta }]);
    } catch (err) {
      setMensajes(prev => [...prev, { rol: 'bot', texto: 'Hubo un error de conexión con el agente médico.' }]);
    } finally {
      setCargando(false);
    }
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
              <p className="whitespace-pre-wrap">{msg.texto}</p>
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

      {/* Input de chat */}
      <form onSubmit={enviarMensaje} className="p-4 bg-white border-t border-gray-200 flex gap-2">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-full px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          placeholder="Escribe tus síntomas aquí..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
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