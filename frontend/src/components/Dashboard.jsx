import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileAudio, Video, FileText, History, Settings, Plus, Download, Bell, Mic, StopCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api/client';

const Dashboard = () => {
  // --- ÉTATS ---
  const [mediaId, setMediaId] = useState(null);
  const [status, setStatus] = useState('idle'); 
  const [progress, setProgress] = useState(0);
  const [originalName, setOriginalName] = useState("");
  const [history, setHistory] = useState([]);
  const [isLive, setIsLive] = useState(false);

  // --- RÉFÉRENCES (Pour le micro) ---
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);

  // --- 1. LOGIQUE : Progression simulée ---
  useEffect(() => {
    let timer;
    if (status === "processing") {
      timer = setInterval(() => {
        setProgress(oldProgress => {
          if (oldProgress >= 95) return 95;
          const diff = Math.random() * 5;
          return Math.min(oldProgress + diff, 95);
        });
      }, 800);
    } else if (status === "ready") {
      setProgress(100);
    } else if (status === "idle") {
      setProgress(0);
    }
    return () => clearInterval(timer);
  }, [status]);

  // --- 2. LOGIQUE : Historique ---
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/media/');
        setHistory(res.data);
      } catch (err) {
        console.error("Erreur historique:", err);
      }
    };
    fetchHistory();
  }, [status]);

  // --- 3. LOGIQUE : Upload Fichier ---
  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile || status === 'processing') return;

    setOriginalName(selectedFile.name);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      setStatus('uploading');
      setProgress(10);
      const response = await api.post('/media/upload', formData);
      setMediaId(response.data.id);
      setStatus('processing');
    } catch (err) {
      alert("Erreur lors de l'envoi.");
      setStatus('idle');
    }
  };

  // --- 4. LOGIQUE : Mode Live ---
  const toggleLive = async () => {
    if (!isLive) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        
        const chunks = [];
        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) chunks.push(e.data);
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(chunks, { type: 'audio/webm' });
          console.log("Enregistrement terminé, Blob créé:", audioBlob);
          setStatus('ready'); // Temporaire en attendant le backend
        };

        mediaRecorder.start();
        setIsLive(true);
        setStatus('processing');
        setOriginalName("Dictée en direct en cours...");
      } catch (err) {
        alert("Impossible d'accéder au micro.");
      }
    } else {
      if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
      if (streamRef.current) streamRef.current.getTracks().forEach(track => track.stop());
      setIsLive(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0f121d] text-white font-sans overflow-hidden">
      
      {/* SIDEBAR */}
      <aside className="w-64 bg-[#161b2c] flex flex-col p-6 border-r border-gray-800">
        <div className="flex items-center gap-2 mb-10">
          <div className="bg-blue-600 p-1.5 rounded-lg shadow-lg shadow-blue-500/20">
             <Mic size={24} />
          </div>
          <span className="text-xl font-bold tracking-tight">SmartScribe</span>
        </div>

        <nav className="flex-1 space-y-2">
          <button 
            disabled={status === 'processing' && !isLive}
            onClick={toggleLive}
            className={`w-full flex items-center justify-center gap-3 p-3 rounded-xl transition font-bold mb-6 ${
              isLive ? 'bg-red-500 animate-pulse' : 'bg-blue-600 hover:bg-blue-500'
            } ${status === 'processing' && !isLive ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {isLive ? <StopCircle size={20} /> : <Mic size={20} />}
            {isLive ? "Arrêter l'écoute" : "Démarrer Live"}
          </button>
          
          <div className="space-y-1">
            <p className="text-[10px] uppercase text-gray-500 font-bold ml-3 mb-2 tracking-widest">Entrées</p>
            <NavItem icon={<Mic size={20}/>} label="Dictée Directe" color={isLive ? "text-red-400" : "text-gray-400"} />
            <NavItem icon={<FileAudio size={20}/>} label="Audio & Podcast" color="text-blue-400" />
            <NavItem icon={<Video size={20}/>} label="Vidéos & Conf" color="text-purple-400" />
            <NavItem icon={<FileText size={20}/>} label="Analyse Document" color="text-green-400" />
          </div>

          <hr className="border-gray-800 my-6" />
          <NavItem icon={<History size={20}/>} label="Bibliothèque" />
          <NavItem icon={<Settings size={20}/>} label="Paramètres" />
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col p-8 relative overflow-y-auto">
        
        <header className="flex justify-between items-center mb-12">
            <div>
                <h1 className="text-2xl font-bold">Bonjour 👋</h1>
                <p className="text-gray-400 text-sm">Prêt pour une prise de notes intelligente ?</p>
            </div>
            <div className="flex gap-4">
               <div className="p-2 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700 transition"><Bell size={20}/></div>
               <div className="w-10 h-10 bg-gradient-to-tr from-blue-500 to-purple-600 rounded-full border-2 border-gray-700 shadow-lg"></div>
            </div>
        </header>

        {/* Action Cards */}
        <div className="grid grid-cols-3 gap-6 max-w-5xl mx-auto w-full mb-10">
          <ActionCard icon={<Mic size={32}/>} title="Mode Live" desc="Capture directe du son." btnColor="bg-red-600" onClick={toggleLive} disabled={status === 'processing'} />
          <ActionCard icon={<FileAudio size={32}/>} title="Audio / Vidéo" desc="Importez vos médias." btnColor="bg-blue-600" onClick={() => document.getElementById('fileInput').click()} disabled={status === 'processing'} />
          <ActionCard icon={<FileText size={32}/>} title="Documents" desc="Analysez vos PDF." btnColor="bg-green-600" disabled={status === 'processing'} />
        </div>

        {/* Drop Zone */}
        <input 
          id="fileInput" 
          type="file" 
          hidden 
          onChange={handleFileUpload} 
          disabled={status === 'processing' || isLive}
          accept="video/*,audio/*,.pdf,.docx,.txt" 
        />
        <motion.div 
          whileHover={status === 'idle' ? { scale: 1.005 } : {}}
          onClick={() => status === 'idle' && document.getElementById('fileInput').click()}
          className={`max-w-5xl mx-auto w-full border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center backdrop-blur-sm mb-8 transition-all ${
            status === 'idle' ? 'border-gray-800 bg-[#161b2c]/30 cursor-pointer hover:border-blue-500/50' : 'border-blue-500/30 bg-blue-500/5 cursor-default'
          }`}
        >
          <Upload size={32} className={`${status !== 'idle' ? 'text-blue-500 animate-bounce' : 'text-gray-500'} mb-4`} />
          <h2 className="text-lg font-medium text-gray-300">
            {status === 'idle' ? "Glissez un média ou document" : originalName}
          </h2>
        </motion.div>

        {/* Status Bar */}
        <div className="max-w-5xl mx-auto w-full bg-[#161b2c] p-6 rounded-2xl border border-gray-800 flex items-center justify-between mb-12 shadow-xl">
          <div className="flex-1 max-w-md">
            <div className="flex justify-between mb-2 text-xs font-bold uppercase tracking-widest">
                <span className="text-blue-400">{status === 'ready' ? "Terminé" : status === 'processing' ? "IA en action" : "Prêt"}</span>
                <span className="text-gray-500">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
              <motion.div animate={{ width: `${progress}%` }} className="h-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
            </div>
          </div>
          <div className="flex gap-3 ml-8">
            <ExportButton label="PDF" disabled={status !== 'ready'} />
            <ExportButton label="DOCX" disabled={status !== 'ready'} />
          </div>
        </div>

        {/* Bibliothèque */}
        <div className="max-w-5xl mx-auto w-full pb-10">
          <h3 className="text-xl font-bold flex items-center gap-2 mb-6">
              <History size={20} className="text-blue-400" /> Bibliothèque
          </h3>
          <div className="grid gap-3">
            {history.length > 0 ? history.map((item) => (
              <div key={item.id} className="bg-[#161b2c] p-4 rounded-xl border border-gray-700 flex justify-between items-center hover:bg-[#1c233a] transition group">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-gray-800 rounded-lg group-hover:text-blue-400">
                    {item.media_type === 'video' ? <Video size={18}/> : <FileAudio size={18}/>}
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{item.filename}</p>
                    <p className="text-[10px] text-gray-500 uppercase">{new Date(item.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                    <span className={`text-[10px] font-black px-2 py-1 rounded ${item.status === 'ready' ? 'text-green-400 bg-green-400/10' : 'text-blue-400 bg-blue-400/10'}`}>
                        {item.status.toUpperCase()}
                    </span>
                    <Download size={16} className="text-gray-600 hover:text-white cursor-pointer" />
                </div>
              </div>
            )) : <div className="text-center py-10 text-gray-600 text-sm">Aucun document traité.</div>}
          </div>
        </div>
      </main>
    </div>
  );
};

// --- SOUS-COMPOSANTS ---
const NavItem = ({ icon, label, color = "text-gray-400" }) => (
  <div className={`flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 cursor-pointer transition ${color}`}>
    {icon} <span className="text-gray-300 font-medium text-sm">{label}</span>
  </div>
);

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
);

const ExportButton = ({ label, disabled }) => (
  <button disabled={disabled} className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition border border-gray-700 ${disabled ? "bg-gray-900 text-gray-600 cursor-not-allowed" : "bg-gray-800 text-white hover:bg-gray-700"}`}>
    <Download size={14} /> {label}
  </button>
);

export default Dashboard;