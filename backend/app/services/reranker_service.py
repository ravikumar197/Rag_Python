from sentence_transformers import CrossEncoder


class RerankerService:
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: list,
        top_k: int = 3
    ):
        if not results:
            return []

        pairs = []

        for result in results:
            chunk = result.DocumentChunk

            pairs.append(
                [
                    query,
                    chunk.content
                ]
            )

        scores = self.model.predict(pairs)

        reranked = []

        for result, score in zip(results, scores):
            reranked.append(
                {
                    "result": result,
                    "score": float(score)
                }
            )

        reranked.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return reranked[:top_k]