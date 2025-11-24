from src.config.env import AppConfig
from azure.cosmos import CosmosClient
import uuid
from datetime import datetime
from loguru import logger

class CosmosDB:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = CosmosClient(self.config.COSMOSDB_ENDPOINT, self.config.COSMOSDB_KEY)
        self.database = self.client.get_database_client(self.config.COSMOSDB_DATABASE)
        self.container = self.database.get_container_client(self.config.COSMOSDB_CONTAINER)

    def insert_items(self, vector, candidate_id, name, skills, work_history, education_history):
        chat_item = {
            'id': str(uuid.uuid4()),
            'candidateId': candidate_id,
            'name': name,
            'embeddings': vector,
            'skills': skills,
            'workHistory': work_history,
            'educationHistory': education_history,
            'timestamp': datetime.utcnow().isoformat(),
        }
        response = self.container.create_item(body=chat_item)
        return response

    def query_items(self, query_vector, num_results: int = 5):
        try:
            query = f"""
            SELECT TOP @num_results c.id, c.candidateId, c.name,
            VectorDistance(c.embeddings, @embedding) AS SimilarityScore 
            FROM c 
            ORDER BY VectorDistance(c.embeddings, @embedding)
            """
            items = self.container.query_items(
                query=query,
                parameters=[
                    {"name": "@num_results", "value": num_results},
                    {"name": "@embedding", "value": query_vector}
                ],
                enable_cross_partition_query=True
            )

            recommendations = []
            for item in items:
                recommendations.append({
                    "id": item.get("id"),
                    "candidate_id": item.get("candidateId"),
                    "name": item.get("name"),
                    "similarity_score": item.get("SimilarityScore")
                })

            return recommendations
        except Exception as e:
            logger.error(f"Error querying items: {e}")
            raise ValueError(f"Error querying items: {e}")