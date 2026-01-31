import React, { useEffect, useState } from 'react'
import { History, FileText, FileAudio, Video } from 'lucide-react'
import api from '../api/client.jsx'

const HistoryPage = () => {
  const [media, setMedia] = useState([])
  const [notes, setNotes] = useState([])

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const [mediaRes, notesRes] = await Promise.all([
          api.get('/history/media'),
          api.get('/history/notes'),
        ])
        setMedia(mediaRes.data)
        setNotes(notesRes.data)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error(err)
        alert('Erreur lors du chargement de l’historique.')
      }
    }
    fetchHistory()
  }, [])

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <section>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <History size={20} className="text-blue-400" />
          Médias traités
        </h2>
        <div className="bg-[#161b2c] border border-gray-800 rounded-2xl p-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-gray-400 uppercase border-b border-gray-800">
              <tr>
                <th className="py-2 text-left">Type</th>
                <th className="py-2 text-left">Nom</th>
                <th className="py-2 text-left">Taille</th>
                <th className="py-2 text-left">Statut</th>
                <th className="py-2 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {media.map((m) => (
                <tr key={m.id} className="border-b border-gray-900 last:border-none">
                  <td className="py-2">
                    <span className="inline-flex items-center gap-1 text-xs text-gray-300">
                      {m.media_type === 'video' ? <Video size={14} /> : <FileAudio size={14} />}
                      {m.media_type}
                    </span>
                  </td>
                  <td className="py-2 text-gray-200">{m.filename}</td>
                  <td className="py-2 text-gray-400 text-xs">
                    {m.size ? `${(m.size / (1024 * 1024)).toFixed(1)} Mo` : '—'}
                  </td>
                  <td className="py-2 text-xs">
                    <span
                      className={`px-2 py-1 rounded-full ${
                        m.status === 'completed'
                          ? 'bg-green-500/10 text-green-400'
                          : 'bg-blue-500/10 text-blue-300'
                      }`}
                    >
                      {m.status}
                    </span>
                  </td>
                  <td className="py-2 text-gray-400 text-xs">
                    {m.created_at ? new Date(m.created_at).toLocaleString() : ''}
                  </td>
                </tr>
              ))}
              {media.length === 0 && (
                <tr>
                  <td className="py-4 text-center text-gray-500 text-xs" colSpan={5}>
                    Aucun média dans l’historique.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <FileText size={20} className="text-green-400" />
          Notes générées
        </h2>
        <div className="bg-[#161b2c] border border-gray-800 rounded-2xl p-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-gray-400 uppercase border-b border-gray-800">
              <tr>
                <th className="py-2 text-left">Titre</th>
                <th className="py-2 text-left">Type</th>
                <th className="py-2 text-left">Statut</th>
                <th className="py-2 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {notes.map((n) => (
                <tr key={n.id} className="border-b border-gray-900 last:border-none">
                  <td className="py-2 text-gray-200">{n.title}</td>
                  <td className="py-2 text-xs text-gray-400">{n.content_type}</td>
                  <td className="py-2 text-xs">
                    <span
                      className={`px-2 py-1 rounded-full ${
                        n.status === 'completed'
                          ? 'bg-green-500/10 text-green-400'
                          : 'bg-blue-500/10 text-blue-300'
                      }`}
                    >
                      {n.status}
                    </span>
                  </td>
                  <td className="py-2 text-gray-400 text-xs">
                    {n.created_at ? new Date(n.created_at).toLocaleString() : ''}
                  </td>
                </tr>
              ))}
              {notes.length === 0 && (
                <tr>
                  <td className="py-4 text-center text-gray-500 text-xs" colSpan={4}>
                    Aucune note dans l’historique.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

export default HistoryPage

