import React, { useEffect, useState } from 'react'
import { FileText, RefreshCcw, Sparkles, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import api from '../api/client.jsx'

const NotesPage = () => {
  const [notes, setNotes] = useState([])
  const [transcriptions, setTranscriptions] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(null) // ID de la transcription en cours de génération
  const [page, setPage] = useState(0) // Page actuelle (commence à 0)  
  const [hasMore, setHasMore] = useState(true) // Y a-t-il d'autres pages ?

  const fetchNotes = async () => {  
    setLoading(true)  
    try {  
      const limit = 20  
      const skip = page * limit  
      const res = await api.get(`/notes/?skip=${skip}&limit=${limit}`)  
      setNotes(res.data)  
      setHasMore(res.data.length === limit) // S'il y a exactement 'limit' résultats, il y a peut-être plus  
      if (res.data.length && !selected) setSelected(res.data[0])  
    } catch (err) {  
      console.error(err)  
      alert('Erreur lors du chargement des notes (es-tu authentifié ?).')  
    } finally {  
      setLoading(false)  
    }  
  }

  const fetchTranscriptions = async () => {
    try {
      const res = await api.get('/history/transcriptions')
      setTranscriptions(res.data)
    } catch (err) {
      console.error('Erreur chargement transcriptions:', err)
    }
  }

  useEffect(() => {  
    fetchNotes()  
    fetchTranscriptions()  
    // eslint-disable-next-line react-hooks/exhaustive-deps  
  }, [page]) // Recharger quand la page change

  // 🆕 Handler pour générer des notes
  const handleGenerateNotes = async (transcriptionId, contentType = 'auto') => {
    setGenerating(transcriptionId)
    try {
      const res = await api.post(`/notes/generate/${transcriptionId}`, null, {
        params: { content_type: contentType }
      })
      
      // Rafraîchir la liste des notes
      await fetchNotes()
      
      // Sélectionner automatiquement la nouvelle note
      setSelected(res.data)
      
      alert('✅ Notes générées avec succès !')
    } catch (err) {
      console.error('Erreur génération notes:', err)
      alert('❌ Erreur lors de la génération des notes.')
    } finally {
      setGenerating(null)
    }
  }

  // 🆕 Handler pour régénérer une note existante
  const handleRegenerateNote = async (noteId) => {
    if (!confirm('Voulez-vous vraiment régénérer cette note ?')) return
    
    setGenerating(noteId)
    try {
      await api.post(`/notes/${noteId}/regenerate`)
      await fetchNotes()
      alert('✅ Note régénérée avec succès !')
    } catch (err) {
      console.error('Erreur régénération:', err)
      alert('❌ Erreur lors de la régénération.')
    } finally {
      setGenerating(null)
    }
  }

  // Vérifier si une transcription a déjà une note
  const hasNote = (transcriptionId) => {
    return notes.some(note => note.transcription_id === transcriptionId)
  }

  return (
    <div className="flex gap-6 h-full">
      {/* Sidebar gauche : Notes + Transcriptions sans notes */}
      <aside className="w-72 bg-[#161b2c] border border-gray-800 rounded-2xl p-4 flex flex-col overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <FileText size={18} className="text-blue-400" />
            Mes notes
          </h2>
          <button
            onClick={fetchNotes}
            className="p-1 rounded-lg bg-gray-800 hover:bg-gray-700 transition text-gray-300"
            title="Rafraîchir"
          >
            <RefreshCcw size={14} />
          </button>
        </div>

        {/* Liste des notes existantes */}
        <div className="flex-1 space-y-2 text-sm">
          {loading && <p className="text-gray-500 text-xs">Chargement…</p>}
          
          {!loading && notes.length === 0 && (
            <p className="text-gray-500 text-xs">Aucune note générée pour le moment.</p>
          )}
          
          {notes.map((note) => (
            <div key={note.id} className="space-y-1">
              <button
                type="button"
                onClick={() => setSelected(note)}
                className={`w-full text-left px-3 py-2 rounded-xl border text-xs ${
                  selected?.id === note.id
                    ? 'bg-blue-500/10 border-blue-500/40 text-blue-100'
                    : 'bg-[#111522] border-gray-800 text-gray-300 hover:bg-[#1b2236]'
                }`}
              >
                <p className="font-semibold truncate">{note.title}</p>
                <p className="text-[10px] text-gray-500 mt-1">
                  {note.content_type} • {note.created_at ? new Date(note.created_at).toLocaleDateString() : ''}
                </p>
              </button>
              
              {/* Bouton Régénérer pour chaque note */}
              <button
                onClick={() => handleRegenerateNote(note.id)}
                disabled={generating === note.id}
                className="w-full px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 transition text-xs text-gray-300 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {generating === note.id ? (
                  <>
                    <Loader2 size={12} className="animate-spin" />
                    Régénération...
                  </>
                ) : (
                  <>
                    <RefreshCcw size={12} />
                    Régénérer
                  </>
                )}
              </button>
            </div>
          ))}
        </div>

        {/* 🆕 Section : Transcriptions sans notes */}
        {transcriptions.length > 0 && (
          <>
            <hr className="border-gray-800 my-4" />
            <h3 className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-2">
              <Sparkles size={14} className="text-yellow-400" />
              Générer des notes
            </h3>
            <div className="space-y-2">
              {transcriptions
                .filter(trans => !hasNote(trans.id))
                .map((trans) => (
                  <div key={trans.id} className="bg-[#111522] border border-gray-800 rounded-xl p-3">
                    <p className="text-xs text-gray-300 mb-2 truncate">
                      Transcription {trans.id.slice(0, 8)}...
                    </p>
                    <button
                      onClick={() => handleGenerateNotes(trans.id)}
                      disabled={generating === trans.id}
                      className="w-full px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 transition text-xs text-white flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {generating === trans.id ? (
                        <>
                          <Loader2 size={12} className="animate-spin" />
                          Génération...
                        </>
                      ) : (
                        <>
                          <Sparkles size={12} />
                          Générer les notes
                        </>
                      )}
                    </button>
                  </div>
                ))}
              
              {transcriptions.every(trans => hasNote(trans.id)) && (
                <p className="text-xs text-gray-500">
                  Toutes les transcriptions ont déjà des notes.
                </p>
              )}
            </div>
          </>
        )}

        {/* 🆕 Contrôles de pagination */}  
        {notes.length > 0 && (  
          <>  
            <hr className="border-gray-800 my-4" />  
            <div className="flex items-center justify-between text-xs">  
              <button  
                onClick={() => setPage(p => Math.max(0, p - 1))}  
                disabled={page === 0}  
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 transition text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"  
              >  
                <ChevronLeft size={14} />  
                Précédent  
              </button>  
                
              <span className="text-gray-500">Page {page + 1}</span>  
                
              <button  
                onClick={() => setPage(p => p + 1)}  
                disabled={!hasMore}  
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 transition text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"  
              >  
                Suivant  
                <ChevronRight size={14} />  
              </button>  
            </div>  
          </>  
        )}
      </aside>

      {/* Panel droit : Contenu de la note sélectionnée */}
      <section className="flex-1 bg-[#161b2c] border border-gray-800 rounded-2xl p-6 overflow-y-auto">
        {selected ? (
          <>
            <h2 className="text-lg font-semibold mb-2">{selected.title}</h2>
            <p className="text-xs text-gray-500 mb-4">
              Type: {selected.content_type} • Statut: {selected.status}
            </p>
            <article className="prose prose-invert max-w-none text-sm">
              <pre className="whitespace-pre-wrap font-sans text-gray-100 text-sm">
                {selected.content}
              </pre>
            </article>
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm">
            Sélectionne une note dans la liste à gauche.
          </div>
        )}
      </section>
    </div>
  )
}

export default NotesPage