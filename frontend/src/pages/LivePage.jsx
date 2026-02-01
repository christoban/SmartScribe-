import React, { useState, useRef } from 'react'
import { Mic, StopCircle, Radio } from 'lucide-react'
import api from '../api/client.jsx'

const LivePage = () => {
  const [sessionId, setSessionId] = useState(null)
  const [status, setStatus] = useState('idle') // 'idle', 'running', 'stopped'
  const [transcription, setTranscription] = useState('')
  
  // Références pour WebSocket et MediaRecorder
  const wsRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const streamRef = useRef(null)

  const startSession = async () => {
    try {
      // 1. Démarrer la session backend
      const res = await api.post('/live/start')
      const newSessionId = res.data.session_id
      setSessionId(newSessionId)
      setStatus('running')
      setTranscription('')
      
      console.log('✅ Session démarrée:', newSessionId)
      
      // 2. Connexion WebSocket
      const wsUrl = `ws://localhost:8000/api/v1/live/stream/${newSessionId}`
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        console.log('🔌 WebSocket connecté')
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'transcription') {
          // Mise à jour de la transcription partielle
          setTranscription(prev => prev + ' ' + data.text)
          console.log('📝 Transcription reçue:', data.text)
        } else if (data.type === 'error') {
          console.error('❌ Erreur WebSocket:', data.message)
          alert(`Erreur: ${data.message}`)
        }
      }
      
      ws.onerror = (error) => {
        console.error('❌ Erreur WebSocket:', error)
        alert('Erreur de connexion WebSocket')
      }
      
      ws.onclose = () => {
        console.log('🔌 WebSocket fermé')
      }
      
      // 3. Démarrer la capture audio
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      })
      mediaRecorderRef.current = mediaRecorder
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
          // Envoyer le chunk audio au WebSocket
          ws.send(event.data)
          console.log('🎙️ Chunk audio envoyé:', event.data.size, 'bytes')
        }
      }
      
      // Envoyer des chunks toutes les 2 secondes
      mediaRecorder.start(2000)
      console.log('🎙️ Enregistrement démarré')
      
    } catch (err) {
      console.error(err)
      alert('Impossible de démarrer la session Live. Vérifiez les permissions micro.')
      setStatus('idle')
    }
  }

  const stopSession = async () => {
    if (!sessionId) return
    
    try {
      // 1. Arrêter l'enregistrement
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
      
      // 2. Arrêter le stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
      
      // 3. Fermer le WebSocket
      if (wsRef.current) {
        wsRef.current.close()
      }
      
      // 4. Arrêter la session backend
      await api.post(`/live/stop/${sessionId}`)
      
      setStatus('stopped')
      console.log('🛑 Session arrêtée')
      
    } catch (err) {
      console.error(err)
      alert('Erreur lors de l\'arrêt de la session Live.')
    }
  }

  const handleClick = () => {
    if (status === 'running') {
      stopSession()
    } else {
      startSession()
    }
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
          disabled={status === 'stopped'}
          className={`px-6 py-3 rounded-xl text-sm font-semibold flex items-center gap-2 ${
            status === 'running'
              ? 'bg-red-600 hover:bg-red-500'
              : status === 'stopped'
              ? 'bg-gray-600 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-500'
          }`}
        >
          {status === 'running' ? <StopCircle size={18} /> : <Mic size={18} />}
          {status === 'running' ? 'Arrêter la session' : status === 'stopped' ? 'Session terminée' : 'Démarrer le Live'}
        </button>
        {sessionId && (
          <p className="text-xs text-gray-500 mt-4">
            ID de session:&nbsp;
            <span className="font-mono text-blue-300">{sessionId}</span>
          </p>
        )}
      </section>

      {/* Zone de transcription en temps réel */}
      {status === 'running' && (
        <section className="bg-[#161b2c] border border-gray-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Radio size={20} className="text-blue-400" />
            Transcription en temps réel
          </h3>
          <div className="bg-[#0f121d] rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto">
            <p className="text-sm text-gray-300 whitespace-pre-wrap">
              {transcription || 'En attente de transcription...'}
            </p>
          </div>
        </section>
      )}

      {/* Transcription finale après arrêt */}
      {status === 'stopped' && transcription && (
        <section className="bg-[#161b2c] border border-gray-800 rounded-2xl p-6">
          <h3 className="font-semibold mb-3 text-green-400">
            ✅ Transcription finale
          </h3>
          <div className="bg-[#0f121d] rounded-lg p-4 max-h-[400px] overflow-y-auto">
            <p className="text-sm text-gray-300 whitespace-pre-wrap">
              {transcription}
            </p>
          </div>
        </section>
      )}

      <section className="bg-[#161b2c] border border-gray-800 rounded-2xl p-6 flex items-start gap-4">
        <Radio size={20} className="text-blue-400 mt-1" />
        <div>
          <h3 className="font-semibold mb-1">WebSocket streaming (actif)</h3>
          <p className="text-sm text-gray-400">
            Le système capture l'audio en temps réel via <code className="text-blue-300">MediaRecorder</code>, 
            envoie les chunks au WebSocket <code className="text-blue-300">/live/stream/&lt;session_id&gt;</code>, 
            et affiche la transcription au fur et à mesure.
          </p>
        </div>
      </section>
    </div>
  )
}

export default LivePage
