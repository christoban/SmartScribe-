"""  
Routes pour l'export de notes (PDF, DOCX, TXT)  
"""  
from fastapi import APIRouter, Depends, HTTPException, Response  
from fastapi.responses import FileResponse  
from typing import Optional, List  
from app.api.deps import get_current_user  
from app.db.repositories.note_repo import NoteRepository  
from app.db.repositories.export_repo import ExportRepository  
from app.db.mongo import get_database  # 🔧 CORRECTION BLOQUANTE : Import ajouté  
from app.schemas.export import ExportOut, ExportCreate  
from app.core.logger import get_logger  
from app.services.export.pdf import generate_pdf  
from app.services.export.docx import generate_docx  
from app.services.export.txt import generate_txt  
  
  
router = APIRouter()  
logger = get_logger("routes.export")  
  
  
@router.post("/{note_id}", response_model=ExportOut)  
async def export_note(  
    note_id: str,  
    format: str = "pdf",  # pdf, docx, txt  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    """  
    Exporte une note dans le format demandé  
    """  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    note_repo = NoteRepository(db)  
    note = await note_repo.get_by_id(note_id)  
    if not note or str(note.user_id) != str(current_user.id):  
        raise HTTPException(status_code=404, detail="Note non trouvée")  
      
    # Préparer les données pour l'export  
    note_data = {  
        "title": note.title,  
        "content": note.content  
    }  
  
    # Générer le fichier d'export  
    if format == "pdf":  
        file_path, file_size = await generate_pdf(note_data)  
    elif format == "docx":  
        file_path, file_size = await generate_docx(note_data)  
    elif format == "txt":  
        file_path, file_size = await generate_txt(note_data)  
    else:  
        raise HTTPException(status_code=400, detail=f"Format {format} non supporté")  
  
    export_data = ExportCreate(  
        note_id=note_id,  
        format=format,  
        file_path=str(file_path),  
        file_size=file_size,  
        user_id=str(current_user.id)  
    )  
      
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    export_repo = ExportRepository(db)  
    export_id = await export_repo.create(export_data.model_dump())  
      
    logger.info("📄 Export %s créé pour note %s", format, note_id)  
      
    return await export_repo.get_by_id(export_id)  
  
@router.get("/{export_id}/download")  
async def download_export(  
    export_id: str,  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    """Télécharge un fichier d'export"""  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    export_repo = ExportRepository(db)  
    export = await export_repo.get_by_id(export_id)  
    if not export or str(export.user_id) != str(current_user.id):  
        raise HTTPException(status_code=404, detail="Export non trouvé")  
      
    from pathlib import Path  
    file_path = Path(export.file_path)  
      
    if not file_path.exists():  
        raise HTTPException(status_code=404, detail="Fichier d'export introuvable")  
      
    media_type_map = {  
        "pdf": "application/pdf",  
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  
        "txt": "text/plain"  
    }  
      
    return FileResponse(  
        path=str(file_path),  
        media_type=media_type_map.get(export.format, "application/octet-stream"),  
        filename=f"export_{export_id}.{export.format}"  
    )  
  
@router.get("/", response_model=List[ExportOut])  
async def list_exports(  
    note_id: Optional[str] = None,  
    current_user = Depends(get_current_user),  
    db = Depends(get_database)  # 🔧 CORRECTION BLOQUANTE : Ajout de la dépendance DB  
):  
    """Liste tous les exports de l'utilisateur"""  
    # 🔧 CORRECTION BLOQUANTE : Utilisation du pattern instance  
    export_repo = ExportRepository(db)  
    if note_id:  
        return await export_repo.get_by_note_id(note_id, str(current_user.id))  
    return await export_repo.get_user_exports(str(current_user.id))