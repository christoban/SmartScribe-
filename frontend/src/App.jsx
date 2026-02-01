import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import './App.css'
import DashboardPage from './pages/DashboardPage.jsx'
import UploadPage from './pages/UploadPage.jsx'
import LivePage from './pages/LivePage.jsx'
import NotesPage from './pages/NotesPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import RegisterPage from './pages/RegisterPage.jsx'
import MainLayout from './components/layout/MainLayout.jsx'
import { UserProvider } from './contexts/UserContext.jsx' // 🔧 AJOUT  


function App() {
  return (
    <UserProvider> {/* 🔧 AJOUT : Enveloppe toute l'app */}  
      <Routes>
        {/* Routes publiques */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Routes protégées sous MainLayout */}
        <Route element={<RequireAuthLayout />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/upload" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/live" element={<LivePage />} />
            <Route path="/notes" element={<NotesPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Route>
        </Route>
      </Routes>
    </UserProvider>  
  )
}

function RequireAuthLayout() {
  const hasToken = Boolean(localStorage.getItem('token'))
  if (!hasToken) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}

export default App

