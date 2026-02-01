import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { UserPlus, Mail, Lock, User } from 'lucide-react'
import api from '../api/client.jsx'

const RegisterPage = () => {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    // Validation : correspondance des mots de passe
    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas.')
      return
    }

    // Validation : longueur minimale du mot de passe
    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères.')
      return
    }

    // 🔧 AMÉLIORATION : Validation de full_name si fourni
    if (fullName && fullName.trim().length > 0 && fullName.trim().length < 2) {
      setError('Le nom complet doit contenir au moins 2 caractères.')
      return
    }

    // 🔧 AMÉLIORATION : Validation de full_name si trop long
    if (fullName && fullName.trim().length > 100) {
      setError('Le nom complet ne peut pas dépasser 100 caractères.')
      return
    }

    setLoading(true)
    try {
      await api.post('/auth/register', {
        email,
        // 🔧 AMÉLIORATION : Envoyer null au lieu de undefined si vide
        full_name: fullName.trim() || null,
        password,
      })

      // Rediriger vers la page de connexion
      navigate('/login', { replace: true })
    } catch (err) {
      console.error(err)
      
      // 🔧 AMÉLIORATION : Messages d'erreur plus spécifiques
      const status = err?.response?.status
      const detail = err?.response?.data?.detail
      
      if (status === 400 && detail?.includes('email')) {
        setError('Cet email est déjà enregistré.')
      } else if (status === 422) {
        setError('Données invalides. Vérifiez vos informations.')
      } else {
        setError(detail || "Impossible de créer le compte. Essayez un autre email.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f121d] text-white">
      <div className="w-full max-w-md bg-[#161b2c] border border-gray-800 rounded-2xl p-8 shadow-xl">
        <div className="flex flex-col items-center mb-6">
          <div className="bg-green-600 p-2 rounded-xl mb-3 shadow-lg shadow-green-500/30">
            <UserPlus size={24} />
          </div>
          <h1 className="text-2xl font-bold">Créer un compte</h1>
          <p className="text-sm text-gray-400 mt-1 text-center">
            Inscrivez-vous pour utiliser SmartScribe.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block text-sm">
            <span className="flex items-center gap-2 text-gray-300 mb-1">
              <User size={16} /> Nom complet (optionnel)
            </span>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#0f1524] border border-gray-700 focus:outline-none focus:border-green-500 text-sm"
              placeholder="Votre nom complet"
            />
          </label>

          <label className="block text-sm">
            <span className="flex items-center gap-2 text-gray-300 mb-1">
              <Mail size={16} /> Email
            </span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#0f1524] border border-gray-700 focus:outline-none focus:border-green-500 text-sm"
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
              className="w-full px-3 py-2 rounded-lg bg-[#0f1524] border border-gray-700 focus:outline-none focus:border-green-500 text-sm"
              placeholder="Au moins 8 caractères"
            />
          </label>

          <label className="block text-sm">
            <span className="flex items-center gap-2 text-gray-300 mb-1">
              <Lock size={16} /> Confirmation
            </span>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-[#0f1524] border border-gray-700 focus:outline-none focus:border-green-500 text-sm"
              placeholder="Répétez le mot de passe"
            />
          </label>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 rounded-lg bg-green-600 hover:bg-green-500 text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
          >
            {loading ? 'Création du compte...' : "S'inscrire"}
          </button>
        </form>

        <p className="mt-4 text-xs text-gray-400 text-center">
          Vous avez déjà un compte ?{' '}
          <Link to="/login" className="text-blue-400 hover:underline">
            Se connecter
          </Link>
        </p>
      </div>
    </div>
  )
}

export default RegisterPage
