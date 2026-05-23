import { useEffect, useState } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';

function App() {
  const [userSession, setUserSession] = useState(null);
  const [currentView, setCurrentView] = useState('login'); // 'login' o 'register'

  useEffect(() => {
    const savedSession = localStorage.getItem('userSession');
    if (savedSession) {
      try {
        const parsed = JSON.parse(savedSession);
        if (parsed && parsed.id_plan) {
          setUserSession(parsed);
        }
      } catch {
        localStorage.removeItem('userSession');
      }
    }
  }, []);

  const handleLoginSuccess = (session) => {
    setUserSession(session);
    localStorage.setItem('userSession', JSON.stringify(session));
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