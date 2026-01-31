import React, { useState } from 'react'
import { Mic, StopCircle, Radio } from 'lucide-react'
import api from '../api/client.jsx'

const LivePage = () => {
  const [sessionId, setSessionId] = useState(null)
  const [status, setStatus] = useState('idle')

  const startSession = async () => {
    try {
      const res = await api.post('/live/start')
      setSessionId(res.data.session_id)
      setStatus('running')
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      alert('Impossible de démarrer la session Live (vérifie que tu es connecté).')
    }
  }

  const stopSession = async () => {
    if (!sessionId) return
    try {
      await api.post(`/live/stop/${sessionId}`)
      setStatus('stopped')
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      alert('Erreur lors de l’arrêt de la session Live.')
    }
  }

  const handleClick = () => {
    if (status === 'running') stopSession()
    else startSession()
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <section className="bg-[#161b2c] border border-gray-800 rounded-2xl p-8 flex flex-col items-center text-center shadow-xl">
        <div className="mb-4 text-red-400">
          {status === 'running' ? <StopCircle size={48} /> : <Mic size={48} />}
        </div>
        <h2 className="text-2xl font-bold mb-2">Mode Live</h2>
        <p className="text-sm text-gray-400 max-w-xl mb-6">
          Démarrez une session pour que SmartScribe écoute votre cours en direct, puis génère automatiquement les
          notes et supports.
        </p>
        <button
          onClick={handleClick}
          className={`px-6 py-3 rounded-xl text-sm font-semibold flex items-center gap-2 ${
            status === 'running'
              ? 'bg-red-600 hover:bg-red-500'
              : 'bg-blue-600 hover:bg-blue-500'
          }`}
        >
          {status === 'running' ? <StopCircle size={18} /> : <Mic size={18} />}
          {status === 'running' ? 'Arrêter la session' : 'Démarrer le Live'}
        </button>
        {sessionId && (
          <p className="text-xs text-gray-500 mt-4">
            ID de session:&nbsp;
            <span className="font-mono text-blue-300">{sessionId}</span>
          </p>
        )}
      </section>

      <section className="bg-[#161b2c] border border-gray-800 rounded-2xl p-6 flex items-start gap-4">
        <Radio size={20} className="text-blue-400 mt-1" />
        <div>
          <h3 className="font-semibold mb-1">WebSocket streaming (backend prêt)</h3>
          <p className="text-sm text-gray-400">
            Le backend expose également un WebSocket sur <code className="text-blue-300">/live/stream/&lt;session_id&gt;</code>{' '}
            pour recevoir le flux audio en temps réel. Tu pourras plus tard connecter ici un{' '}
            <code>MediaRecorder</code> qui envoie les chunks audio vers ce WebSocket pour une transcription continue.
          </p>
        </div>
      </section>
    </div>
  )
}

export default LivePage

