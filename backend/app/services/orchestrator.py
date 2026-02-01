import shutil
from pathlib import Path
from typing import Optional, Sequence
import asyncio
import re

from app.core.config import settings
from app.core.logger import get_logger
from app.services.media.audio_processor import audio_processor
from app.services.media.noise_cleaner import NoiseCleaner
from app.services.media.video_analyzer import video_analyzer

from app.services.ia.transcriber import transcriber
from app.services.ia.vision_client import vision_client
from app.services.ia.manager import ia_manager

from app.services.nlp.text_cleaner import text_cleaner
from app.services.nlp.document_structurer import document_structurer
from app.db.repositories.transcription_repo import TranscriptionRepository
from app.db.repositories.note_repo import NoteRepository
from app.db.repositories.export_repo import ExportRepository
from app.models.transcription import Transcription
from app.db.mongo import get_database
from app.models.note import Note

from app.services.export.pdf import generate_pdf
from app.services.export.docx import generate_docx
from app.services.export.txt import generate_txt

# 🔧 CORRECTION FACULTATIVE : Validation des formats d'export
VALID_EXPORT_FORMATS = {"pdf", "docx", "txt"}

class Orchestrator:
    def __init__(self):
        self._repo = None       # Pour les transcriptions
        self._note_repo = None  # Pour les notes
        self._export_repo = None
        self._logger = get_logger("orchestrator")
    
    @property
    def repo(self) -> TranscriptionRepository:
        """Propriété pour le repository des transcriptions"""
        if self._repo is None:
            db = get_database()
            self._repo = TranscriptionRepository(db)
        return self._repo

    @property
    def note_repo(self) -> NoteRepository:
        """Propriété pour le repository des notes"""
        if self._note_repo is None:
            db = get_database()
            self._note_repo = NoteRepository(db)
        return self._note_repo
    
    @property
    def export_repo(self) -> ExportRepository:
        """Propriété pour le repository des exports"""
        if self._export_repo is None:
            db = get_database()
            self._export_repo = ExportRepository(db)
        return self._export_repo
    
    async def process_full_media(
        self,
        media_id: str,
        file_path: Path,
        user_id: Optional[str] = None,
        content_type: Optional[str] = None,
        export_formats: Optional[Sequence[str]] = None,
    ) -> bool:
        """
        Pipeline complet:
        Upload → Traitement média → Transcription → OCR/Vision → Structuration NLP → Export → Sauvegarde DB
        """
        # 🔧 CORRECTION FACULTATIVE : Validation et normalisation des formats d'export
        if not export_formats:
            export_formats = ["pdf", "docx", "txt"]
            self._logger.warning("⚠️ Aucun format d'export reçu. Forçage par défaut : PDF, DOCX, TXT")
        else:
            # Valider et filtrer les formats invalides
            export_formats = [fmt.lower() for fmt in export_formats if fmt.lower() in VALID_EXPORT_FORMATS]
            if not export_formats:
                self._logger.warning("⚠️ Aucun format valide fourni. Utilisation des formats par défaut.")
                export_formats = ["pdf", "docx", "txt"]

        temp_files: list[Path] = []
        temp_dirs: list[Path] = []

        try:
            self._logger.info("🚀 Pipeline démarré: media_id=%s", media_id)

            # 1) Media → audio
            await self.repo.update_status(media_id, "processing_audio")
            extracted_audio_path: Path = await asyncio.to_thread(audio_processor.extract_audio, file_path)
            temp_files.append(extracted_audio_path)

            # 2) Nettoyage audio (noise reduction)
            cleaned_audio_str = await NoiseCleaner.clean_audio(str(extracted_audio_path))
            cleaned_audio_path = Path(cleaned_audio_str)
            temp_files.append(cleaned_audio_path)

            # 3) Vision (si vidéo): keyframes → OCR
            keyframes: list[Path] = []
            keyframes_dir = None  # 🔧 CORRECTION BLOQUANTE : Initialisation pour éviter UnboundLocalError
            if file_path.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm"}:
                keyframes_dir = settings.FRAMES_DIR / media_id
                temp_dirs.append(keyframes_dir)
                keyframes = await asyncio.to_thread(
                    video_analyzer.extract_keyframes,
                    file_path,
                    keyframes_dir,
                    2,  # interval_seconds
                    None,
                )

            visual_context = await vision_client.get_visual_context(keyframes)

            # 4) STT → Transcription par morceaux (Chunking)
            await self.repo.update_status(media_id, "transcribing")

            # On découpe l'audio nettoyé en segments de 10 min
            chunks = await asyncio.to_thread(audio_processor.split_audio, cleaned_audio_path)
            temp_files.extend(chunks) # On ajoute les chunks pour le nettoyage final
            
            full_raw_text = []
            full_refined_text = []
            all_segments = []
            detected_language = "fr"

            self._logger.info("📦 Audio divisé en %s segments", len(chunks))

            for i, chunk_path in enumerate(chunks):
                self._logger.info("🎙️ Transcription segment %d/%d...", i + 1, len(chunks))
                
                # Transcription du morceau
                stt_chunk = await transcriber.process_audio_to_text(chunk_path)
                
                # Accumulation des résultats
                if stt_chunk.get("raw_text"):
                    full_raw_text.append(stt_chunk["raw_text"])
                if stt_chunk.get("refined_text"):
                    full_refined_text.append(stt_chunk["refined_text"])
                
                # On récupère la langue du premier chunk
                if i == 0:
                    detected_language = stt_chunk.get("language", "fr")
                
                # Optionnel: on agrège les segments temporels si besoin
                all_segments.extend(stt_chunk.get("segments", []))

            # Fusion finale des textes
            raw_transcript = "\n".join(full_raw_text)
            refined_transcript = "\n".join(full_refined_text)

            if not refined_transcript:
                raise ValueError("La transcription a échoué : aucun texte généré.")
            
            # 5) Type contenu (si auto)
            effective_content_type = content_type or "auto"
            if effective_content_type == "auto":
                effective_content_type = await ia_manager.detect_content_type(refined_transcript)

            await self.repo.update_status(media_id, "generating_notes")

            # 6) Génération notes (Markdown)
            generated_notes = await ia_manager.generate_notes(
                transcription=refined_transcript,
                content_type=effective_content_type,
                visual_context=visual_context,
            )
            generated_notes = text_cleaner.clean(generated_notes)

            # --- 🔧 CORRECTION BLOQUANTE : Sauvegarde permanente des images AVANT nettoyage ---
            if keyframes:
                # On définit un dossier permanent pour les images de cette note
                permanent_img_dir = Path(settings.STORAGE_DIR) / "notes_assets" / media_id
                permanent_img_dir.mkdir(parents=True, exist_ok=True)
                
                saved_paths = []
                for img in keyframes:
                    dest = permanent_img_dir / img.name
                    shutil.copy(img, dest) # On copie l'image vers le stockage permanent
                    saved_paths.append(dest)
                
                # 🔧 CORRECTION IMPORTANTE : Utiliser les chemins permanents pour l'intégration
                generated_notes = self._integrate_real_captures(generated_notes, saved_paths)
                
                # 🔧 CORRECTION BLOQUANTE : Retirer keyframes_dir de temp_dirs pour éviter 
                # la suppression prématurée des images sources avant la copie complète
                if keyframes_dir and keyframes_dir in temp_dirs:
                    temp_dirs.remove(keyframes_dir)

            # 7) Structuration NLP (pré-export)
            structured = document_structurer.structure_for_export(
                generated_notes,
                content_type=effective_content_type,
                metadata={"media_id": media_id, "user_id": user_id},
            )

            # 8) DB: transcription (texte transcrit) + note (texte généré)
            transcription_obj = Transcription(
                media_id=media_id,
                user_id=user_id,
                text=refined_transcript,           # Texte fusionné
                raw_text=raw_transcript,            # Texte brut fusionné
                visual_context=visual_context,
                segments=all_segments,
                language=detected_language,
                model="SmartScribe (Whisper Chunked + OCR + LLM)",
            )

            saved_transcription = await self.repo.create(transcription_obj)

            # Création de l'objet Note proprement
            new_note = Note(
                user_id=user_id,
                transcription_id=str(saved_transcription.id),
                media_id=media_id,
                title=structured.get("title", "Notes de cours"),
                content=structured.get("raw_content", generated_notes),
                content_type=effective_content_type,
                generation_params={"visual": bool(visual_context)},
                model_used="groq:llama-3.3-70b",
                status="completed"
            )

            # Appel via l'instance du repo (self.note_repo)
            saved_note = await self.note_repo.create(new_note)
            note_id = saved_note.id # Récupération de l'ID pour les exports

            # --- 🔧 CORRECTION IMPORTANTE : Gestion d'erreurs robuste pour les exports ---
            if export_formats:
                final_content = structured.get("raw_content") or generated_notes
                final_title = structured.get("title") or "Notes de cours"
                
                note_data = {
                    "title": final_title, 
                    "content": final_content
                }
                
                export_results = []
                for fmt in export_formats:
                    fmt = fmt.lower()
                    try:
                        self._logger.info(f"⏳ Génération de l'export {fmt}...")
                        
                        # Génération du fichier selon le format
                        if fmt == "pdf":
                            export_path, file_size = await generate_pdf(note_data)
                        elif fmt == "docx":
                            export_path, file_size = await generate_docx(note_data)
                        elif fmt == "txt":
                            export_path, file_size = await generate_txt(note_data)
                        else:
                            self._logger.warning(f"Format {fmt} non supporté, ignoré")
                            continue
                        
                        # 🔧 CORRECTION IMPORTANTE : Vérifier que le fichier existe réellement
                        if not Path(export_path).exists():
                            raise FileNotFoundError(f"Le fichier {export_path} n'a pas été créé")
                        
                        # Sauvegarde en base de données
                        export_id = await self.export_repo.create({
                            "user_id": user_id,
                            "note_id": str(note_id),
                            "format": fmt,
                            "file_path": str(export_path),
                            "file_size": file_size,
                        })
                        
                        export_results.append({"format": fmt, "id": export_id})
                        self._logger.info(f"✅ Export {fmt} créé : {export_path}")
                        
                    except Exception as e:
                        # 🔧 CORRECTION IMPORTANTE : Logger l'erreur complète sans bloquer le pipeline
                        self._logger.error(f"❌ Erreur lors de l'export {fmt} : {str(e)}", exc_info=True)
                        # Ne pas bloquer le pipeline pour un export raté
                        continue
                
                # 🔧 CORRECTION IMPORTANTE : Log du résultat global
                if export_results:
                    self._logger.info(f"✅ {len(export_results)} export(s) créé(s) avec succès")
                else:
                    self._logger.warning("⚠️ Aucun export n'a pu être créé")
                    
            self._logger.info("✅ Pipeline terminé avec succès: media_id=%s", media_id)
            return True

        except Exception as e:
            self._logger.error("❌ ÉCHEC CRITIQUE du pipeline media_id=%s: %s", media_id, str(e))
            # Optionnel : loguer la stacktrace complète ici pour le debug
            import traceback
            self._logger.error(traceback.format_exc())
            return False

        finally:
            # Nettoyage systématique des fichiers temporaires (audio découpé, etc.)
            self._logger.info("🧹 Nettoyage des fichiers temporaires...")
            self._cleanup(temp_files, temp_dirs)

    async def process_document(  
        self,  
        media_id: str,  
        file_path: Path,  
        user_id: Optional[str] = None,  
        content_type: Optional[str] = None,  
        export_formats: Optional[Sequence[str]] = None,  
    ) -> bool:  
        """  
        🆕 Pipeline pour documents textuels (PDF, DOCX, TXT):  
        Upload → Extraction texte → Génération notes → Structuration NLP → Export → Sauvegarde DB  
        """  
        # Validation des formats d'export  
        if not export_formats:  
            export_formats = ["pdf", "docx", "txt"]  
            self._logger.warning("⚠️ Aucun format d'export reçu. Forçage par défaut : PDF, DOCX, TXT")  
        else:  
            export_formats = [fmt.lower() for fmt in export_formats if fmt.lower() in VALID_EXPORT_FORMATS]  
            if not export_formats:  
                self._logger.warning("⚠️ Aucun format valide fourni. Utilisation des formats par défaut.")  
                export_formats = ["pdf", "docx", "txt"]  
  
        try:  
            self._logger.info("🚀 Pipeline document démarré: media_id=%s", media_id)  
  
            # 1) Extraction du texte selon le format  
            await self.repo.update_status(media_id, "extracting_text")  
              
            file_ext = file_path.suffix.lower()  
            if file_ext == ".pdf":  
                from app.services.document.text_extractor import extract_text_from_pdf  
                text_content = await extract_text_from_pdf(file_path)  
            elif file_ext in [".docx", ".doc"]:  
                from app.services.document.text_extractor import extract_text_from_docx  
                text_content = await extract_text_from_docx(file_path)  
            elif file_ext == ".txt":  
                from app.services.document.text_extractor import extract_text_from_txt  
                text_content = await extract_text_from_txt(file_path)  
            else:  
                raise ValueError(f"Format de document non supporté: {file_ext}")  
              
            if not text_content or len(text_content.strip()) < 50:  
                raise ValueError("Le document ne contient pas assez de texte exploitable")  
              
            self._logger.info(f"📄 Texte extrait: {len(text_content)} caractères")  
  
            # 2) Détection du type de contenu  
            effective_content_type = content_type or "auto"  
            if effective_content_type == "auto":  
                effective_content_type = await ia_manager.detect_content_type(text_content)  
                self._logger.info("🔍 Type détecté: %s", effective_content_type)  
              
            # 3) Génération de notes via IA  
            await self.repo.update_status(media_id, "generating_notes")  
            generated_notes = await ia_manager.generate_notes(  
                transcript=text_content,  
                content_type=effective_content_type,  
                visual_context=None  # Pas de contexte visuel pour les documents  
            )  
              
            # 4) Nettoyage du texte  
            cleaned_notes = text_cleaner.clean(generated_notes)  
              
            # 5) Structuration pour export  
            structured = document_structurer.structure_for_export(  
                cleaned_notes,  
                content_type=effective_content_type,  
                metadata={"media_id": media_id, "user_id": user_id},  
            )  
              
            # 6) Sauvegarde en base de données  
            from app.models.transcription import Transcription  
            transcription_obj = Transcription(  
                media_id=media_id,  
                user_id=user_id,  
                text=text_content,  
                raw_text=text_content,  
                visual_context=None,  
                segments=[],  
                language="fr",  
                model_name="Document Extraction",  
            )  
              
            saved_transcription = await self.repo.create(transcription_obj)  
              
            # 7) Création de la note  
            from app.models.note import Note  
            new_note = Note(  
                user_id=user_id,  
                transcription_id=str(saved_transcription.id),  
                media_id=media_id,  
                title=structured.get("title", "Notes de document"),  
                content=structured.get("raw_content", cleaned_notes),  
                content_type=effective_content_type,  
                generation_params={"source": "document"},  
                model_used="groq:llama-3.3-70b",  
                status="completed"  
            )  
              
            saved_note = await self.note_repo.create(new_note)  
            note_id = saved_note.id  
              
            # 8) Exports  
            if export_formats:  
                final_content = structured.get("raw_content") or cleaned_notes  
                final_title = structured.get("title") or "Notes de document"  
                  
                note_data = {  
                    "title": final_title,  
                    "content": final_content  
                }  
                  
                export_results = []  
                for fmt in export_formats:  
                    fmt = fmt.lower()  
                    try:  
                        self._logger.info(f"⏳ Génération de l'export {fmt} pour document...")  
                          
                        if fmt == "pdf":  
                            export_path, file_size = await generate_pdf(note_data)  
                        elif fmt == "docx":  
                            export_path, file_size = await generate_docx(note_data)  
                        elif fmt == "txt":  
                            export_path, file_size = await generate_txt(note_data)  
                        else:  
                            self._logger.warning(f"⚠️ Format {fmt} non supporté, ignoré")  
                            continue  
                          
                        # Vérification que le fichier a bien été créé  
                        if not Path(export_path).exists():  
                            self._logger.error(f"❌ Le fichier d'export {fmt} n'a pas été créé")  
                            continue  
                          
                        # Sauvegarde en base de données  
                        export_id = await self.export_repo.create({  
                            "user_id": user_id,  
                            "note_id": str(note_id),  
                            "format": fmt,  
                            "file_path": str(export_path),  
                            "file_size": file_size,  
                        })  
                          
                        export_results.append({"format": fmt, "id": export_id})  
                        self._logger.info(f"✅ Export {fmt} créé : {export_path}")  
                          
                    except Exception as e:  
                        self._logger.error(f"❌ Erreur lors de l'export {fmt} : {str(e)}", exc_info=True)  
                        continue  
                  
                if export_results:  
                    self._logger.info(f"✅ {len(export_results)} export(s) créé(s) avec succès")  
                else:  
                    self._logger.warning("⚠️ Aucun export n'a pu être créé")  
              
            self._logger.info("✅ Pipeline document terminé avec succès: media_id=%s", media_id)  
            return True  
              
        except Exception as e:  
            self._logger.error("❌ ÉCHEC CRITIQUE du pipeline document media_id=%s: %s", media_id, str(e))  
            import traceback  
            self._logger.error(traceback.format_exc())  
            return False  
  
    def _cleanup(self, files: list[Path], dirs: list[Path]) -> None:  
        """Nettoyage rigoureux des fichiers et dossiers temporaires."""  
        for f in files:  
            if f and f.exists():  
                try:   
                    f.unlink()  
                except Exception:   
                    pass  
          
        for d in dirs:  
            if d and d.exists():  
                try:   
                    shutil.rmtree(d)  
                except Exception:   
                    pass  
  
    def _integrate_real_captures(self, content: str, keyframes: list[Path]) -> str:  
        """  
        🔧 CORRECTION IMPORTANTE : Gestion des chemins d'images pour exports PDF/DOCX  
          
        Scanne le document pour trouver ' изображение ' et y injecter   
        les captures d'écran réelles de la vidéo.  
          
        Note : Utilise le chemin absolu pour que les générateurs PDF/DOCX   
        puissent localiser et embarquer les images correctement.  
        """  
        # Pattern flexible pour capturer la balise avec espaces possibles  
        tag_pattern = r"\s? изображение \s?"  
          
        # On sépare le contenu pour traiter chaque occurrence  
        parts = re.split(tag_pattern, content)  
          
        if len(parts) == 1:  
            return content  # Pas de balise trouvée  
          
        new_content = parts[0]  
        for i in range(1, len(parts)):  
            # Si on a encore des images disponibles  
            if i-1 < len(keyframes):  
                img_path = keyframes[i-1]  
                # Utilisation du chemin absolu pour que les générateurs PDF/DOCX  
                # puissent localiser les images sur le disque  
                img_tag = f"\n\n![Illustration technique {i}]({img_path.absolute()})\n\n"  
                new_content += img_tag + parts[i]  
            else:  
                # Plus d'images ? On retire simplement la balise  
                new_content += parts[i]  
                  
        return new_content  
  
orchestrator = Orchestrator()
