import { useEffect, useState } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';

function App() {
  const [userSession, setUserSession] = useState(null);
  const [currentView, setCurrentView] = useState('login'); // 'login' o 'register'
  const SESSION_MS = 5 * 60 * 1000;

  useEffect(() => {
    const savedSession = localStorage.getItem('userSession');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        const expiresAt = Number(parsed?.expiresAt || 0);
        if (parsed && parsed.id_plan && expiresAt > Date.now()) {
          setUserSession(parsed);
        } else {
          localStorage.removeItem('userSession');
        }
      } catch {
        localStorage.removeItem('userSession');
      }
    }
  }, []);

  useEffect(() => {
    if (!userSession?.expiresAt) return;

    const intervalId = setInterval(() => {
      if (Date.now() >= userSession.expiresAt) {
        setUserSession(null);
        localStorage.removeItem('userSession');
      }
    }, 30000);

    return () => clearInterval(intervalId);
  }, [userSession]);

  const handleLoginSuccess = (session) => {
    const sessionWithExpiry = {
      ...session,
      expiresAt: Date.now() + SESSION_MS
    };
    setUserSession(sessionWithExpiry);
    localStorage.setItem('userSession', JSON.stringify(sessionWithExpiry));
  };

  const handleLogout = () => {
    setUserSession(null);
    localStorage.removeItem('userSession');
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* Navbar simple */}
      <header className="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
        <h1 className="text-xl font-bold">Estimador Médico IA</h1>
        {userSession && (
          <div className="flex items-center gap-4">
            <span className="text-sm">
              Hola, {userSession.nombres}
              {userSession.nombre_plan ? ` | Plan: ${userSession.nombre_plan}` : ''}
            </span>
            <button 
              onClick={handleLogout}
              className="text-xs bg-blue-800 px-3 py-1 rounded hover:bg-blue-900 transition"
            >
              Salir
            </button>
          </div>
        )}
      </header>

      {/* Renderizado Condicional */}
      <main className="max-w-4xl mx-auto p-4 flex-grow flex flex-col justify-center">
        {!userSession ? (
          currentView === 'login' ? (
            <Login onLoginSuccess={handleLoginSuccess} onToggleView={setCurrentView} />
          ) : (
            <Register onToggleView={setCurrentView} />
          )
        ) : (
          <Chat idPlan={userSession.id_plan} />
        )}
      </main>
    </div>
  );
}

export default App;