import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileAudio, Video, FileText, History, Download, Mic, Loader2 } from 'lucide-react'

import api from '../api/client.jsx'

const ALLOWED_MEDIA_EXT = ['mp4', 'mp3', 'wav', 'm4a', 'mov', 'webm', 'mkv']
const ALLOWED_DOC_EXT = ['pdf', 'docx', 'txt', 'doc']

const UploadPage = () => {
  const [mediaId, setMediaId] = useState(null)
  const [status, setStatus] = useState('idle')
  const [progress, setProgress] = useState(0)
  const [exportingFormat, setExportingFormat] = useState(null) // 'pdf', 'docx', 'txt' ou null
  const [originalName, setOriginalName] = useState('')
  const [history, setHistory] = useState([])
  const [uploadType, setUploadType] = useState(null) // 'media' ou 'document'

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
        console.error('Erreur historique:', err)
      }
    }
    fetchHistory()
  }, [status])

  // 🔧 NOUVEAU : Handler pour upload de médias (audio/vidéo)
  const handleMediaUpload = async (e) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile || status === 'processing') return

    const ext = selectedFile.name.split('.').pop().toLowerCase()
    if (!ALLOWED_MEDIA_EXT.includes(ext)) {
      alert(`Format .${ext} non supporté pour les médias. Formats acceptés : ${ALLOWED_MEDIA_EXT.join(', ')}`)
      return
    }

    setOriginalName(selectedFile.name)
    setUploadType('media')
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setStatus('uploading')
      setProgress(10)
      const response = await api.post('/media/upload', formData)
      setMediaId(response.data.id)
      setStatus('processing')
    } catch (err) {
      console.error(err)
      alert("Erreur lors de l'envoi du fichier média.")
      setStatus('idle')
    }
  }

  // 🔧 NOUVEAU : Handler pour upload de documents (PDF/DOCX/TXT)
  const handleDocumentUpload = async (e) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile || status === 'processing') return

    const ext = selectedFile.name.split('.').pop().toLowerCase()
    if (!ALLOWED_DOC_EXT.includes(ext)) {
      alert(`Format .${ext} non supporté pour les documents. Formats acceptés : ${ALLOWED_DOC_EXT.join(', ')}`)
      return
    }

    setOriginalName(selectedFile.name)
    setUploadType('document')
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      setStatus('uploading')
      setProgress(10)
      const response = await api.post('/documents/upload', formData)
      setMediaId(response.data.id)
      setStatus('processing')
    } catch (err) {
      console.error(err)
      alert("Erreur lors de l'envoi du document.")
      setStatus('idle')
    }
  }

  const handleExport = async (format) => {  
    if (!mediaId || status !== 'ready' || exportingFormat) return  
      
    setExportingFormat(format)  
      
    try {  
      // 1. Récupérer la note associée au media_id  
      const notesRes = await api.get(`/notes/?transcription_id=${mediaId}`)  
        
      if (!notesRes.data || notesRes.data.length === 0) {  
        alert("Aucune note trouvée pour ce média. Générez d'abord les notes.")  
        setExportingFormat(null)  
        return  
      }  
        
      const noteId = notesRes.data[0].id  
        
      // 2. Créer l'export  
      const exportRes = await api.post(`/export/${noteId}?format=${format}`)  
      const exportId = exportRes.data.id  
        
      // 3. Télécharger le fichier  
      const downloadUrl = `/export/${exportId}/download`  
      window.open(`${api.defaults.baseURL}${downloadUrl}`, '_blank')  
        
    } catch (err) {  
      console.error('Erreur export:', err)  
      alert(`Erreur lors de l'export ${format.toUpperCase()}`)  
    } finally {  
      setExportingFormat(null)  
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
          onClick={() => document.getElementById('mediaInput').click()}
          disabled={status === 'processing'}
        />
        <ActionCard
          icon={<FileText size={32} />}
          title="Documents"
          desc="Analysez vos PDF, DOCX, TXT."
          btnColor="bg-green-600"
          onClick={() => document.getElementById('documentInput').click()}
          disabled={status === 'processing'}
        />
      </div>

      {/* 🔧 NOUVEAU : Input séparé pour médias */}
      <input
        id="mediaInput"
        type="file"
        hidden
        onChange={handleMediaUpload}
        disabled={status === 'processing'}
        accept="video/*,audio/*"
      />

      {/* 🔧 NOUVEAU : Input séparé pour documents */}
      <input
        id="documentInput"
        type="file"
        hidden
        onChange={handleDocumentUpload}
        disabled={status === 'processing'}
        accept=".pdf,.docx,.txt,.doc"
      />

      <motion.div
        whileHover={status === 'idle' ? { scale: 1.005 } : {}}
        onClick={() => {
          if (status === 'idle') {
            // Par défaut, ouvrir le sélecteur de médias
            document.getElementById('mediaInput').click()
          }
        }}
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
        {status !== 'idle' && uploadType && (
          <p className="text-xs text-gray-500 mt-2">
            Type : {uploadType === 'media' ? 'Média (Audio/Vidéo)' : 'Document (PDF/DOCX/TXT)'}
          </p>
        )}
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
          <ExportButton   
            label="PDF"   
            format="pdf"  
            disabled={!isReady || !mediaId}   
            loading={exportingFormat === 'pdf'}  
            onClick={() => handleExport('pdf')}  
          />  
          <ExportButton   
            label="DOCX"   
            format="docx"  
            disabled={!isReady || !mediaId}   
            loading={exportingFormat === 'docx'}  
            onClick={() => handleExport('docx')}  
          />  
          <ExportButton   
            label="TXT"   
            format="txt"  
            disabled={!isReady || !mediaId}   
            loading={exportingFormat === 'txt'}  
            onClick={() => handleExport('txt')}  
          />  
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
                    {item.media_type === 'video' ? <Video size={18} /> : 
                     item.media_type === 'document' ? <FileText size={18} /> : 
                     <FileAudio size={18} />}
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

const ExportButton = ({ label, format, disabled, loading, onClick }) => (  
  <button  
    disabled={disabled || loading}  
    onClick={onClick}  
    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition border border-gray-700 ${  
      disabled || loading   
        ? 'bg-gray-900 text-gray-600 cursor-not-allowed'   
        : 'bg-gray-800 text-white hover:bg-gray-700'  
    }`}  
  >  
    {loading ? (  
      <>  
        <Loader2 size={14} className="animate-spin" />  
        Export...  
      </>  
    ) : (  
      <>  
        <Download size={14} /> {label}  
      </>  
    )}  
  </button>  
)

export default UploadPage