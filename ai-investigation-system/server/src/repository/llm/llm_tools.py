from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ChatCompletionAgent, AgentResponseItem
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
import pyodbc
import pandas as pd
from azure.core.credentials import AzureKeyCredential
import json
from loguru import logger
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from src.config.env import AppConfig
from azure.cosmos import CosmosClient
import numpy as np
import uuid
from datetime import datetime
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from typing import List

class CaseAnalystAgentTools:   
    def __init__(self, config: AppConfig = None):
        self.database_id = "ai-fraud"
        self.container_id = "vectors"
        self.config = config

        try:
            # Initialize Cosmos DB client
            self.client = CosmosClient.from_connection_string(self.config.COSMOS_DB_CONNECTION_STRING)
            self.database = self.client.get_database_client(self.database_id)
            self.container = self.database.get_container_client(self.container_id)
            
            # Initialize Azure OpenAI embedding service
            self.embedding_service = AzureTextEmbedding(
                endpoint=self.config.AZURE_OPENAI_API_BASE,
                api_key=self.config.AZURE_OPENAI_API_KEY,
                deployment_name=self.config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
                api_version=self.config.AZURE_OPENAI_API_VERSION
            )
        except Exception as e:
            logger.error(f"Failed to initialize CaseAnalystAgentTools: {e}")
            raise

    async def embedding(self, text: str) -> List[float]:
        if not self.embedding_service:
            raise ValueError("Embedding service not initialized")
        
        try:
            embeddings = await self.embedding_service.generate_embeddings([text])
            vector = embeddings[0]
            if isinstance(vector, np.ndarray):
                vector = vector.tolist()
        
            return vector
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    @kernel_function(
        name="search_documents",
        description="Search documents in Cosmos DB using semantic search",
    )
    async def search_documents(self, query: str, top_k: int = 5, case_id: str = None) -> list:
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding(query)

            # Search semantic
            VECTOR_FIELD_NAME = "embeddings"

            QUERY_TEMPLATE = f"""
            SELECT TOP @num_results c.id, c.content, c.fileName, c.fileUrl,
            VectorDistance(c.{VECTOR_FIELD_NAME}, @embedding) AS SimilarityScore 
            FROM c 
            WHERE c.caseId = @case_id
            ORDER BY VectorDistance(c.{VECTOR_FIELD_NAME}, @embedding)
            """

            items = list(self.container.query_items(
                query=QUERY_TEMPLATE,
                parameters=[
                    {"name": "@num_results", "value": top_k},
                    {"name": "@embedding", "value": query_embedding},
                    {"name": "@case_id", "value": case_id}
                ],
                enable_cross_partition_query=True
            ))

            results = []
            for item in items:
                result = {
                    "id": item["id"],
                    "content": item["content"],
                    "file_name": item.get("fileName"),
                    "file_url": item.get("fileUrl"),
                    "similarity_score": item["SimilarityScore"]
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic_search: {e}")
            raise


# async def test_semantic_search():
#     """Test the semantic search functionality"""
#     try:
#         # Initialize the search tools
#         search_tools = CaseAnalystAgentTools(config=AppConfig)
        
#         # Test query
#         test_query = "Apa yang terjadi dengan Agri Sentosa dan Food Supply?"
#         print(f"\n{'='*60}")
#         print(f"Testing Semantic Search with query: '{test_query}'")
#         print(f"{'='*60}\n")
        
#         # Perform search
#         results = await search_tools.semantic_search(query=test_query, top_k=5)
        
#         print(f"\nSearch completed successfully!")
#         print(f"Found {len(results) if results else 0} results\n")
        
#     except Exception as e:
#         logger.error(f"Test failed: {e}")
#         print(f"Error: {e}")


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test_semantic_search())
