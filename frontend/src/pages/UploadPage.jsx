import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileAudio, Video, FileText, History, Download, Mic } from 'lucide-react'
import api from '../api/client.jsx'

const ALLOWED_EXT = ['mp4', 'mp3', 'wav', 'm4a', 'mov', 'webm', 'mkv']

const UploadPage = () => {
  const [mediaId, setMediaId] = useState(null)
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState(0)
  const [originalName, setOriginalName] = useState('')
  const [history, setHistory] = useState([])

  // progression simulée
  useEffect(() => {
    let timer
    if (status === 'processing') {
      timer = setInterval(() => {
        setProgress((old) => {
          if (old >= 95) return 95
          const diff = Math.random() * 5
          return Math.min(old + diff, 95)
        })
      }, 800)
    } else if (status === 'ready') {
      setProgress(100)
    } else if (status === 'idle') {
      setProgress(0)
    }
    return () => clearInterval(timer)
  }, [status])

  // historique
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/media/')
        setHistory(res.data)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Erreur historique:', err)
      }
    }
    fetchHistory()
  }, [status])

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile || status === 'processing') return

    const ext = selectedFile.name.split('.').pop().toLowerCase()
    if (!ALLOWED_EXT.includes(ext)) {
      alert(`Format .${ext} non supporté par l'API /media/upload`)
      return
    }

    setOriginalName(selectedFile.name)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setStatus('uploading')
      setProgress(10)
      const response = await api.post('/media/upload', formData)
      setMediaId(response.data.id)
      setStatus('processing')
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      alert("Erreur lors de l'envoi du fichier.")
      setStatus('idle')
    }
  }

  const isReady = status === 'ready'

  return (
    <div className="flex flex-col h-full">
      {/* Cartes d'action */}
      <div className="grid grid-cols-3 gap-6 max-w-5xl mx-auto w-full mb-10">
        <ActionCard
          icon={<Mic size={32} />}
          title="Mode Live"
          desc="Capture directe du son de la salle."
          btnColor="bg-red-600"
          disabled
        />
        <ActionCard
          icon={<FileAudio size={32} />}
          title="Audio / Vidéo"
          desc="Importez vos enregistrements."
          btnColor="bg-blue-600"
          onClick={() => document.getElementById('fileInput').click()}
          disabled={status === 'processing'}
        />
        <ActionCard
          icon={<FileText size={32} />}
          title="Documents"
          desc="Analysez vos PDF, DOCX, TXT."
          btnColor="bg-green-600"
          disabled
        />
      </div>

      {/* Zone de dépôt */}
      <input
        id="fileInput"
        type="file"
        hidden
        onChange={handleFileUpload}
        disabled={status === 'processing'}
        accept="video/*,audio/*,.pdf,.docx,.txt"
      />

      <motion.div
        whileHover={status === 'idle' ? { scale: 1.005 } : {}}
        onClick={() => status === 'idle' && document.getElementById('fileInput').click()}
        className={`max-w-5xl mx-auto w-full border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center backdrop-blur-sm mb-8 transition-all ${
          status === 'idle'
            ? 'border-gray-800 bg-[#161b2c]/30 cursor-pointer hover:border-blue-500/50'
            : 'border-blue-500/30 bg-blue-500/5 cursor-default'
        }`}
      >
        <Upload
          size={32}
          className={`${status !== 'idle' ? 'text-blue-500 animate-bounce' : 'text-gray-500'} mb-4`}
        />
        <h2 className="text-lg font-medium text-gray-300">
          {status === 'idle' ? 'Glissez un média ou document' : originalName}
        </h2>
      </motion.div>

      {/* Barre de statut */}
      <div className="max-w-5xl mx-auto w-full bg-[#161b2c] p-6 rounded-2xl border border-gray-800 flex items-center justify-between mb-12 shadow-xl">
        <div className="flex-1 max-w-md">
          <div className="flex justify-between mb-2 text-xs font-bold uppercase tracking-widest">
            <span className="text-blue-400">
              {isReady ? 'Terminé' : status === 'processing' ? 'IA en action' : 'Prêt'}
            </span>
            <span className="text-gray-500">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
            <motion.div
              animate={{ width: `${progress}%` }}
              className="h-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]"
            />
          </div>
        </div>
        <div className="flex gap-3 ml-8">
          <ExportButton label="PDF" disabled={!isReady || !mediaId} />
          <ExportButton label="DOCX" disabled={!isReady || !mediaId} />
        </div>
      </div>

      {/* Historique */}
      <div className="max-w-5xl mx-auto w-full pb-10">
        <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
          <History size={20} className="text-blue-400" /> Historique des médias
        </h3>
        <div className="grid gap-3">
          {history.length > 0 ? (
            history.map((item) => (
              <div
                key={item.id}
                className="bg-[#161b2c] p-4 rounded-xl border border-gray-700 flex justify-between items-center hover:bg-[#1c233a] transition group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-gray-800 rounded-lg group-hover:text-blue-400">
                    {item.media_type === 'video' ? <Video size={18} /> : <FileAudio size={18} />}
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{item.filename}</p>
                    <p className="text-[10px] text-gray-500 uppercase">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span
                    className={`text-[10px] font-black px-2 py-1 rounded ${
                      item.status === 'completed'
                        ? 'text-green-400 bg-green-400/10'
                        : 'text-blue-400 bg-blue-400/10'
                    }`}
                  >
                    {item.status?.toUpperCase() ?? 'UNKNOWN'}
                  </span>
                  <Download size={16} className="text-gray-600 hover:text-white cursor-pointer" />
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-10 text-gray-600 text-sm">Aucun média traité pour le moment.</div>
          )}
        </div>
      </div>
    </div>
  )
}

const ActionCard = ({ icon, title, desc, btnColor, onClick, disabled }) => (
  <div className="bg-[#1c233a] p-6 rounded-2xl border border-gray-800 flex flex-col items-center text-center shadow-lg">
    <div className={`${btnColor.replace('bg-', 'text-')} mb-4`}>{icon}</div>
    <h3 className="font-bold text-lg">{title}</h3>
    <p className="text-xs text-gray-400 mb-6">{desc}</p>
    <button
      disabled={disabled}
      onClick={onClick}
      className={`${btnColor} w-full py-2 rounded-lg text-sm font-bold hover:opacity-80 transition disabled:opacity-50`}
    >
      {disabled ? 'Patientez...' : 'Sélectionner'}
    </button>
  </div>
)

const ExportButton = ({ label, disabled }) => (
  <button
    disabled={disabled}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition border border-gray-700 ${
      disabled ? 'bg-gray-900 text-gray-600 cursor-not-allowed' : 'bg-gray-800 text-white hover:bg-gray-700'
    }`}
  >
    <Download size={14} /> {label}
  </button>
)

export default UploadPage

