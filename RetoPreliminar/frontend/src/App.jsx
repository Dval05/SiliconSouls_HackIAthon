import { useState } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';

function App() {
  const [userSession, setUserSession] = useState(null);
  const [currentView, setCurrentView] = useState('login'); // 'login' o 'register'

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* Navbar simple */}
      <header className="bg-blue-600 text-white p-4 shadow-md flex justify-between items-center">
        <h1 className="text-xl font-bold">Estimador Médico IA</h1>
        {userSession && (
          <div className="flex items-center gap-4">
            <span className="text-sm">Hola, {userSession.nombres}</span>
            <button 
              onClick={() => setUserSession(null)}
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
            <Login onLoginSuccess={setUserSession} onToggleView={setCurrentView} />
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