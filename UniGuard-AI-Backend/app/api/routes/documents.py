from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.document_service import process_pdf
from app.services.vector_store import get_all_documents, delete_document
from app.core.security import verify_token

router = APIRouter()

@router.post(
    "/documents/upload",
    summary="Upload Enterprise Document",
    description="Uploads static PDF file, parses its text, and vectors it to ChromaDB.",
    dependencies=[Depends(verify_token)]
)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported for Enterprise Document ingestion."
        )
        
    try:
        result_message = await process_pdf(file)
        return {"status": "success", "message": result_message}
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to process document: {e}")

@router.get(
    "/documents/list",
    summary="List all uploaded documents"
)
def list_documents():
    docs = get_all_documents()
    return {"status": "success", "documents": docs}

@router.delete(
    "/documents/{filename}",
    summary="Delete an enterprise document",
    dependencies=[Depends(verify_token)]
)
def remove_document(filename: str):
    try:
        delete_document(filename)
        return {"status": "success", "message": f"Deleted {filename} from vector store."}
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to delete document: {e}")
