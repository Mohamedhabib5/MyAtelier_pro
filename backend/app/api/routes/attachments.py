from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from app.api.deps import require_identity_view
from app.core.config import get_settings

router = APIRouter(tags=['Attachments'])

@router.get('/attachments/{attachment_id}')
async def get_attachment(
    attachment_id: str,
    request: Request,
    user=Depends(require_identity_view)
):
    settings = request.app.state.settings
    storage_dir = Path(settings.attachment_storage_dir).resolve()
    
    file_path = (storage_dir / attachment_id).resolve()
    
    # Protect against path traversal
    if not str(file_path).startswith(str(storage_dir)):
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    return FileResponse(
        file_path, 
        content_disposition_type="inline", 
        headers={"X-Content-Type-Options": "nosniff"}
    )
