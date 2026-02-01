import React, { useEffect, useState } from 'react'
import { Activity, FileText, Radio, History } from 'lucide-react'
import api from '../api/client.jsx'
import { useUser } from '../contexts/UserContext.jsx' // 🔧 AJOUT  

const DashboardPage = () => {
  const [health, setHealth] = useState(null)
  const [mediaCount, setMediaCount] = useState(null)
  const [notesCount, setNotesCount] = useState(null)
  const { user } = useUser() // 🔧 AJOUT  


  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, mediaRes, notesRes] = await Promise.all([
          api.get('/health'),
          api.get('/history/media'),
          api.get('/history/notes'),
        ])
        setHealth(healthRes.data)
        setMediaCount(mediaRes.data.length)
        setNotesCount(notesRes.data.length)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Erreur dashboard:', err)
      }
    }
    fetchData()
  }, [])

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <section>  
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">  
          <Activity size={20} className="text-green-400" />  
          Bonjour {user?.full_name || user?.email?.split('@')[0] || 'Utilisateur'} 👋  
        </h2>  
        <div className="grid grid-cols-3 gap-4">  
          <StatCard  
            label="API SmartScribe"  
            value={health?.status === 'healthy' ? 'En ligne' : 'Inconnue'}  
            badge={health?.status}  
          />  
          <StatCard label="Médias traités" value={mediaCount ?? '…'} />  
          <StatCard label="Notes générées" value={notesCount ?? '…'} />  
        </div>  
      </section>
      <section>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Radio size={20} className="text-blue-400" />
          Vue d’ensemble
        </h2>
        <div className="grid grid-cols-3 gap-6">
          <FeatureCard
            icon={<FileText size={28} />}
            title="Upload & transcription"
            description="Téléversez vos cours audio/vidéo et laissez l’IA produire une transcription propre."
            linkLabel="Aller à l’upload"
            href="/upload"
          />
          <FeatureCard
            icon={<Radio size={28} />}
            title="Mode Live"
            description="Capture en temps réel pendant le cours et notes générées à la volée."
            linkLabel="Ouvrir le mode Live"
            href="/live"
          />
          <FeatureCard
            icon={<History size={28} />}
            title="Bibliothèque"
            description="Retrouvez vos médias, transcriptions et notes passées."
            linkLabel="Voir l’historique"
            href="/history"
          />
        </div>
      </section>
    </div>
  )
}

const StatCard = ({ label, value, badge }) => (
  <div className="bg-[#161b2c] border border-gray-800 rounded-2xl p-5 flex flex-col gap-2">
    <p className="text-xs uppercase tracking-widest text-gray-500 font-semibold">{label}</p>
    <p className="text-2xl font-bold">{value}</p>
    {badge && (
      <span className="inline-flex text-[10px] uppercase font-bold px-2 py-1 rounded bg-green-500/10 text-green-400 w-fit">
        {badge}
      </span>
    )}
  </div>
)

const FeatureCard = ({ icon, title, description, linkLabel, href }) => (
  <a
    href={href}
    className="bg-[#161b2c] border border-gray-800 rounded-2xl p-6 flex flex-col gap-3 hover:bg-[#1c233a] transition"
  >
    <div className="text-blue-400">{icon}</div>
    <h3 className="font-semibold text-lg">{title}</h3>
    <p className="text-sm text-gray-400 flex-1">{description}</p>
    <span className="text-xs font-semibold text-blue-400 mt-2">{linkLabel}</span>
  </a>
)

export default DashboardPage

