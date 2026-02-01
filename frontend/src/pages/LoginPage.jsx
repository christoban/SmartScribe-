import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn, Mail, Lock } from 'lucide-react'
import api from '../api/client.jsx'
import { useUser } from '../contexts/UserContext.jsx' // 🔧 AJOUT  

const LoginPage = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const { fetchUser } = useUser() // 🔧 AJOUT  


  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const form = new FormData()
      form.append('username', email)
      form.append('password', password)

      const res = await api.post('/auth/login', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      const { access_token, refresh_token } = res.data
      localStorage.setItem('token', access_token)
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token)
      }

      // 🔧 AJOUT : Charger les infos utilisateur après login  
      await fetchUser()  

      navigate('/upload', { replace: true })
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      setError("Identifiants invalides ou erreur serveur.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f121d] text-white">
      <div className="w-full max-w-md bg-[#161b2c] border border-gray-800 rounded-2xl p-8 shadow-xl">
        <div className="flex flex-col items-center mb-6">
          <div className="bg-blue-600 p-2 rounded-xl mb-3 shadow-lg shadow-blue-500/30">
            <LogIn size={24} />
          </div>
          <h1 className="text-2xl font-bold">Connexion SmartScribe</h1>
          <p className="text-sm text-gray-400 mt-1 text-center">
            Connectez-vous pour accéder à vos médias, transcriptions et notes.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block text-sm">
            <span className="flex items-center gap-2 text-gray-300 mb-1">
              <Mail size={16} /> Email
            </span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#0f1524] border border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
              placeholder="vous@example.com"
            />
          </label>

          <label className="block text-sm">
            <span className="flex items-center gap-2 text-gray-300 mb-1">
              <Lock size={16} /> Mot de passe
            </span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#0f1524] border border-gray-700 focus:outline-none focus:border-blue-500 text-sm"
              placeholder="Votre mot de passe"
            />
          </label>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
      </div>

      <p className="mt-4 text-xs text-gray-400 text-center">
        Pas encore de compte ?{' '}
        <Link to="/register" className="text-green-400 hover:underline">
          Créer un compte
        </Link>
      </p>
    </div> 
  )
}

export default LoginPage

