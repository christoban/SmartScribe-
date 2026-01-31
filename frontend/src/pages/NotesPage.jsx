import React, { useEffect, useState } from 'react'
import { FileText, RefreshCcw } from 'lucide-react'
import api from '../api/client.jsx'

const NotesPage = () => {
  const [notes, setNotes] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchNotes = async () => {
    setLoading(true)
    try {
      const res = await api.get('/notes/')
      setNotes(res.data)
      if (res.data.length && !selected) setSelected(res.data[0])
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      alert('Erreur lors du chargement des notes (es-tu authentifié ?).')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotes()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="flex gap-6 h-full">
      <aside className="w-72 bg-[#161b2c] border border-gray-800 rounded-2xl p-4 flex flex-col">
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
        <div className="flex-1 space-y-2 overflow-y-auto text-sm">
          {loading && <p className="text-gray-500 text-xs">Chargement…</p>}
          {!loading && notes.length === 0 && (
            <p className="text-gray-500 text-xs">Aucune note générée pour le moment.</p>
          )}
          {notes.map((note) => (
            <button
              key={note.id}
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
          ))}
        </div>
      </aside>

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

