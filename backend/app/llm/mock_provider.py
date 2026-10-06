from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2
    ) -> str:

        return (
            "This is a mock LLM response. "
            "The RAG pipeline successfully built "
            "a prompt from the retrieved context."
        )