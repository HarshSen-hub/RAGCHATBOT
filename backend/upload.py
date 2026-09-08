import os
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from .ingest import ingest_pdf

router = APIRouter(tags=["Upload"])


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs("uploads", exist_ok=True)
    upload_path = f"uploads/{file.filename}"

    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        summary = ingest_pdf(upload_path)
    except ValueError as e:
        
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {
        "message": "PDF ingested successfully",
        "filename": file.filename,
        **summary,
    }
