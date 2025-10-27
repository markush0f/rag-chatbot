from fastapi import APIRouter, Body

from app.domain.rag.service import RagService

router = APIRouter(prefix="/rag", tags=["RAG"])

@router.post("/ask")
def ask_rag(
    question: str = Body(..., embed=True),
    file_ids: list[str] = Body(..., embed=True)
):
    """
    Flujo completo: descarga docs → crea embeddings → responde → limpia → devuelve respuesta.
    """
    rag = RagService()
    try:
        answer = rag.run_pipeline(question, file_ids)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
