import { NavLink, useLocation, Outlet } from 'react-router-dom'
import { Bell, Mic, FileAudio, Video, FileText, History, Settings, LayoutDashboard } from 'lucide-react'

const navItemClasses =
  'flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 cursor-pointer transition text-sm font-medium'

const MainLayout = () => {
  const location = useLocation()

  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <div className="flex h-screen bg-[#0f121d] text-white font-sans overflow-hidden">
      {/* SIDEBAR */}
      <aside className="w-64 bg-[#161b2c] flex flex-col p-6 border-r border-gray-800">
        <div className="flex items-center gap-2 mb-10">
          <div className="bg-blue-600 p-1.5 rounded-lg shadow-lg shadow-blue-500/20">
            <Mic size={24} />
          </div>
          <span className="text-xl font-bold tracking-tight">SmartScribe</span>
        </div>

        <nav className="flex-1 space-y-4 text-gray-300">
          <div>
            <p className="text-[10px] uppercase text-gray-500 font-bold ml-3 mb-2 tracking-widest">Vue globale</p>
            <NavLink
              to="/dashboard"
              className={`${navItemClasses} ${
                isActive('/dashboard') ? 'bg-white/10 text-white' : 'text-gray-400'
              }`}
            >
              <LayoutDashboard size={18} />
              <span>Dashboard</span>
            </NavLink>
          </div>

          <div className="space-y-1">
            <p className="text-[10px] uppercase text-gray-500 font-bold ml-3 mb-2 tracking-widest">Entrées</p>
            <NavLink
              to="/live"
              className={`${navItemClasses} ${
                isActive('/live') ? 'bg-red-500/20 text-red-300' : 'text-gray-400'
              }`}
            >
              <Mic size={18} />
              <span>Mode Live</span>
            </NavLink>
            <NavLink
              to="/upload"
              className={`${navItemClasses} ${
                isActive('/upload') ? 'bg-blue-500/20 text-blue-300' : 'text-gray-400'
              }`}
            >
              <FileAudio size={18} />
              <span>Upload Média</span>
            </NavLink>
            <NavLink
              to="/upload"
              className={`${navItemClasses} text-purple-300`}
            >
              <Video size={18} />
              <span>Vidéos & Conf</span>
            </NavLink>
            <NavLink
              to="/upload"
              className={`${navItemClasses} text-green-300`}
            >
              <FileText size={18} />
              <span>Documents</span>
            </NavLink>
          </div>

          <hr className="border-gray-800 my-4" />

          <NavLink
            to="/history"
            className={`${navItemClasses} ${
              isActive('/history') ? 'bg-white/10 text-white' : 'text-gray-400'
            }`}
          >
            <History size={18} />
            <span>Historique</span>
          </NavLink>

          <NavLink
            to="/notes"
            className={`${navItemClasses} ${
              isActive('/notes') ? 'bg-white/10 text-white' : 'text-gray-400'
            }`}
          >
            <FileText size={18} />
            <span>Notes</span>
          </NavLink>

          <NavLink
            to="/settings"
            className={`${navItemClasses} text-gray-500 pointer-events-none`}
          >
            <Settings size={18} />
            <span>Paramètres (bientôt)</span>
          </NavLink>
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col p-8 overflow-y-auto">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-2xl font-bold">SmartScribe</h1>
            <p className="text-gray-400 text-sm">
              Transformez vos cours et médias en notes intelligentes.
            </p>
          </div>
          <div className="flex gap-4 items-center">
            <div className="p-2 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700 transition">
              <Bell size={20} />
            </div>
            <div className="w-10 h-10 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-full border-2 border-gray-700 shadow-lg" />
          </div>
        </header>

        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout

