import numpy as np


class SimilarityService:

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float]
    ) -> float:

        a = np.array(vector_a)
        b = np.array(vector_b)

        similarity = np.dot(a, b) / (
            np.linalg.norm(a) * np.linalg.norm(b)
        )

        return float(similarity)