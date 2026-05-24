import { useEffect, useState } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';

function App() {
  const [userSession, setUserSession] = useState(null);
  const [currentView, setCurrentView] = useState('login'); // 'login' o 'register'
  const [agentBusy, setAgentBusy] = useState(false);
  const SESSION_MS = 5 * 60 * 1000;

  useEffect(() => {
    const savedSession = localStorage.getItem('userSession');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        const lastActivity = Number(parsed?.lastActivity || 0);
        if (parsed && parsed.id_plan && lastActivity) {
          if (Date.now() - lastActivity <= SESSION_MS) {
            setUserSession(parsed);
          } else {
            localStorage.removeItem('userSession');
          }
        } else {
          localStorage.removeItem('userSession');
        }
      } catch {
        localStorage.removeItem('userSession');
      }
    }
  }, []);

  useEffect(() => {
    if (!userSession?.lastActivity) return;

    const intervalId = setInterval(() => {
      if (!agentBusy && Date.now() - userSession.lastActivity >= SESSION_MS) {
        setUserSession(null);
        localStorage.removeItem('userSession');
      }
    }, 30000);

    return () => clearInterval(intervalId);
  }, [agentBusy, userSession]);

  const handleLoginSuccess = (session) => {
    const sessionWithActivity = {
      ...session,
      lastActivity: Date.now()
    };
    setUserSession(sessionWithActivity);
    localStorage.setItem('userSession', JSON.stringify(sessionWithActivity));
  };

  const handleActivity = () => {
    if (!userSession) return;
    const updated = { ...userSession, lastActivity: Date.now() };
    setUserSession(updated);
    localStorage.setItem('userSession', JSON.stringify(updated));
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
            <Login
              onLoginSuccess={handleLoginSuccess}
              onToggleView={setCurrentView}
              onActivity={handleActivity}
            />
          ) : (
            <Register onToggleView={setCurrentView} onActivity={handleActivity} />
          )
        ) : (
          <Chat
            idPlan={userSession.id_plan}
            onActivity={handleActivity}
            onAgentBusy={setAgentBusy}
          />
        )}
      </main>
    </div>
  );
}

export default App;