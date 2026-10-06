class ContextService:

    def build_context(self, reranked_results):
        context_parts = []

        for index, item in enumerate(
            reranked_results,
            start=1
        ):
            row = item["result"]

            context_parts.append(
                f"""
SOURCE {index}
Page: {row.DocumentChunk.page_number}
Chunk: {row.DocumentChunk.chunk_index}
Vector Distance: {row.distance}
Rerank Score: {item["score"]}

{row.DocumentChunk.content}
"""
            )

        return "\n".join(context_parts)
