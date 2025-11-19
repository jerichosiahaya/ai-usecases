from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
import asyncio
from typing import List, Dict
from dotenv import load_dotenv
from loguru import logger
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from src.repository.database import CosmosDB
from src.repository.embedding import AzureAIEmbedding
from src.domain.candidate_recommendation import CandidateData, JobData

load_dotenv()

class CandidateRecommendation:
    def __init__(self, cosmosdb: CosmosDB, embedding_service: AzureAIEmbedding):
        self.cosmosdb = cosmosdb
        self.embedding_service = embedding_service

    async def recommend(self, job_detail: JobData):
        try:
            embedding = await self.embedding_service.generate_query_embedding(job_detail.get('job_description'))
            result = self.cosmosdb.query_items(embedding)
            return result
        except Exception as e:
            logger.error(f"Error recommending candidates: {e}")
            raise ValueError(f"Error recommending candidates: {e}")

    async def indexing(self, candidate_data: CandidateData):
        try:
            embedding = await self.embedding_service.generate_query_embedding(candidate_data.get('candidate_skills'))
            result = self.cosmosdb.insert_items(
                vector=embedding,
                candidate_id=candidate_data.get('candidate_id'),
                name=candidate_data.get('candidate_name'),
                skills=candidate_data.get('candidate_skills'),
                education_history=candidate_data.get('candidate_education_history'),
                work_history=candidate_data.get('candidate_work_history'),
            )
            return result
        except Exception as e:
            logger.error(f"Error indexing candidate data: {e}")
            raise ValueError(f"Error indexing candidate data: {e}")