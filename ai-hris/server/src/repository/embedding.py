import os
from typing import List
from loguru import logger
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from src.config.env import AppConfig

class AzureAIEmbedding:
    def __init__(self, config: AppConfig):
        self.config = config
        self.embedding_service = AzureTextEmbedding(
            deployment_name=self.config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
            endpoint=self.config.AZURE_OPENAI_API_BASE,
            api_key=self.config.AZURE_OPENAI_API_KEY,
            api_version=self.config.AZURE_OPENAI_API_VERSION
        )

    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query."""
        try:
            embeddings = await self.embedding_service.generate_embeddings([query])
            embedding_vector = embeddings[0]
            
            # Convert to list for JSON serialization
            if hasattr(embedding_vector, 'tolist'):
                return embedding_vector.tolist()
            return list(embedding_vector)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []