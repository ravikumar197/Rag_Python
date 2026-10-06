from sqlalchemy.orm import Session

from app.services.conversation_service import get_messages
from app.services.embedding_service import EmbeddingService
from app.services.vector_retrieval_service import VectorRetrievalService
from app.services.context_service import ContextService
from app.services.reranker_service import RerankerService
from app.llm.base import LLMProvider


class RAGService:

    def __init__(self, llm: LLMProvider):

        self.llm = llm

        embedding_service = EmbeddingService()

        self.retrieval_service = VectorRetrievalService(
            embedding_service
        )

        self.reranker_service = RerankerService()

        self.context_service = ContextService()

    def rewrite_query(
        self,
        query: str,
        conversation_history: list
    ) -> str:

        if not conversation_history:
            return query

        history_text = "\n".join(
            f"{message.role.upper()}: {message.content}"
            for message in conversation_history[-10:]
        )

        prompt = f"""
Rewrite the user's latest question into a standalone
search query for a document retrieval system.

Use the conversation history to resolve references such as:
- it
- this
- that
- he
- she
- they
- the movie
- the previous one

IMPORTANT:
- Preserve exact entity names from the conversation.
- Preserve document identifiers, IDs, codes, movie IDs,
  product IDs, employee IDs, account IDs, etc. when available.
- If the previous answer identified a specific entity,
  include that entity in the rewritten query.
- Do not remove useful identifiers from the conversation.

Rules:
- Return ONLY the rewritten search query.
- Do not answer the question.
- Do not add information that is not present in the conversation.
- Preserve the user's intent.
- Make the query specific enough for semantic retrieval.

Conversation history:
{history_text}

Latest user question:
{query}

Standalone search query:
"""

        rewritten_query = self.llm.generate(
            prompt=prompt,
            temperature=0
        )

        return rewritten_query.strip()

    def answer(
        self,
        db: Session,
        query: str,
        document_id: int,
        conversation_id: int | None = None,
        top_k: int = 5,
        temperature: float = 0.2,
        similarity_threshold: float = 0.60,
        rerank_threshold: float = 0.0
    ):

        # --------------------------------
        # 1. Get conversation history
        # --------------------------------

        conversation_history = []

        if conversation_id:

            messages = get_messages(
                db=db,
                conversation_id=conversation_id
            )

            conversation_history = messages[-10:]

        # --------------------------------
        # 2. Rewrite query
        # --------------------------------

        retrieval_query = self.rewrite_query(
            query=query,
            conversation_history=conversation_history
        )

        print(
            "Original query:",
            query
        )

        print(
            "Retrieval query:",
            retrieval_query
        )

        # --------------------------------
        # 3. Vector retrieval
        # --------------------------------

        candidate_results = self.retrieval_service.retrieve(
            db=db,
            query=retrieval_query,
            document_id=document_id,
            top_k=max(top_k * 3, 10),
            similarity_threshold=similarity_threshold
        )

        print(
            "Vector candidates:",
            len(candidate_results)
        )

        # --------------------------------
        # 4. Cross-Encoder reranking
        # --------------------------------

        reranked_results = self.reranker_service.rerank(
            query=retrieval_query,
            results=candidate_results,
            top_k=top_k
        )

        print(
            "Reranked results:",
            len(reranked_results)
        )

        # --------------------------------
        # 5. Relevance gate
        # --------------------------------

        if not reranked_results:

            return {
                "answer": "I couldn't find that information in the provided documents.",
                "results": []
            }

        top_rerank_score = reranked_results[0]["score"]

        print(
            "Top rerank score:",
            top_rerank_score
        )

        if top_rerank_score < rerank_threshold:

            print(
                "Relevance gate: rejected"
            )

            return {
                "answer": "I couldn't find that information in the provided documents.",
                "results": []
            }

        print(
            "Relevance gate: accepted"
        )

        # --------------------------------
        # 6. Build context
        # --------------------------------

        context = self.context_service.build_context(
            reranked_results
        )

        # --------------------------------
        # 7. Build conversation history
        # --------------------------------

        history_text = "\n".join(
            f"{message.role.upper()}: {message.content}"
            for message in conversation_history
        )

        # --------------------------------
        # 8. Generate final answer
        # --------------------------------

        prompt = f"""
You are an enterprise document assistant.

Use ONLY the information provided in the document context
and conversation history.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- Resolve references using conversation history.
- The document context is the source of truth for factual answers.
- If the answer is not supported by the document context,
  say that the information is not available.
- Answer concisely.

Conversation history:
{history_text}

Document context:
{context}

Current user question:
{query}

Answer:
"""

        answer = self.llm.generate(
            prompt=prompt,
            temperature=temperature
        )

        return {
            "answer": answer,
            "results": reranked_results
        }
