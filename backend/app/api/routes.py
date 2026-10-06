
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.services.conversation_service import (
    create_conversation,
    get_conversation,
    add_message,
)

from app.api.dependencies import get_db
# from app.llm.mock_provider import MockLLMProvider
from app.llm.groq_provider import GroqProvider
from app.services.rag_service import RAGService

from app.schemas.user import UserCreate, UserUpdate
from app.schemas.chat import ChatRequest
from app.schemas.document import DocumentCreate
from app.schemas.search import SearchRequest

from app.services.user_service import (
    create_user,
    get_user,
    update_user,
    delete_user
)

from app.services.document_service import (
    create_document,
    get_document
)

from app.services.embedding_service import EmbeddingService
from app.services.vector_retrieval_service import VectorRetrievalService
from app.services.document_ingestion_service import DocumentIngestionService


router = APIRouter()


@router.get("/")
def root():
    return {
        "message": "Enterprise GenAI Platform API"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    user_id = int(request.user_id)

    # --------------------------------
    # 1. Get or create conversation
    # --------------------------------

    if request.conversation_id:

        conversation = get_conversation(
            db,
            int(request.conversation_id)
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Conversation does not belong to this user"
            )

    else:

        conversation = create_conversation(
            db=db,
            user_id=user_id,
            title=request.message[:255]
        )

    # --------------------------------
    # 2. Run RAG using previous history
    # --------------------------------

    rag_service = RAGService(
        GroqProvider()
    )

    result = rag_service.answer(
        db=db,
        query=request.message,
        document_id=request.document_id,
        conversation_id=conversation.id,
        temperature=request.temperature
    )

    # --------------------------------
    # 3. Save user message
    # --------------------------------

    add_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )

    # --------------------------------
    # 4. Save assistant message
    # --------------------------------

    add_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"]
    )

    # --------------------------------
    # 5. Return response
    # --------------------------------

    return {
        "message": result["answer"],
        "user_id": request.user_id,
        "conversation_id": str(conversation.id),
        "sources": [
            {
                "chunk_index": item["result"].DocumentChunk.chunk_index,
                "page_number": item["result"].DocumentChunk.page_number,
                "content": item["result"].DocumentChunk.content,
                "vector_distance": item["result"].distance,
                "rerank_score": item["score"]
            }
            for item in result["results"]
        ]
    }


@router.post("/users")
def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    new_user = create_user(
        db,
        user
    )

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }


@router.get("/users/{user_id}")
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = get_user(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }


@router.put("/users/{user_id}")
def update_user_route(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):

    user = update_user(
        db,
        user_id,
        user_data
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }


@router.delete("/users/{user_id}")
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = delete_user(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_content = await file.read()

    storage_dir = Path("storage/documents")

    storage_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = storage_dir / file.filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    document_data = DocumentCreate(
        filename=file.filename,
        file_type=file.content_type,
        file_size=len(file_content)
    )

    document = create_document(
        db,
        document_data
    )

    ingestion_service = DocumentIngestionService()

    ingestion_result = ingestion_service.ingest(
        db=db,
        document_id=document.id,
        file_path=str(file_path),
        filename=document.filename,
        file_type=document.file_type
    )

    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "chunks_created": len(
            ingestion_result["chunks"]
        )
    }


@router.post("/search")
def search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):

    service = VectorRetrievalService(
        EmbeddingService()
    )

    results = service.retrieve(
        db=db,
        query=request.query,
        document_id=request.document_id,
        top_k=request.top_k
    )

    return {
        "query": request.query,
        "results": [
            {
                "content": row.DocumentChunk.content,
                "page_number": row.DocumentChunk.page_number,
                "chunk_index": row.DocumentChunk.chunk_index,
                "distance": row.distance
            }
            for row in results
        ]
    }


@router.get("/documents/{document_id}")
def get_document_route(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = get_document(
        db,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "status": document.status,
        "created_at": document.created_at
    }