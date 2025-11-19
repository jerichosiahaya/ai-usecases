import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppConfig:
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', '')
    AZURE_OPENAI_API_BASE: str = os.getenv('AZURE_OPENAI_API_BASE', '')
    AZURE_OPENAI_API_VERSION: str = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    AZURE_OPENAI_API_KEY: str = os.getenv('AZURE_OPENAI_API_KEY', '')

    COSMOSDB_ENDPOINT: str = os.getenv('COSMOSDB_ENDPOINT', '')
    COSMOSDB_KEY: str = os.getenv('COSMOSDB_KEY', '')
    COSMOSDB_CONTAINER: str = os.getenv('COSMOSDB_CONTAINER', '')
    COSMOSDB_DATABASE: str = os.getenv('COSMOSDB_DATABASE', '')

    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002')
    AZURE_OPENAI_EMBEDDING_API_VERSION: str = os.getenv('AZURE_OPENAI_EMBEDDING_API_VERSION', '2024-02-15-preview')
    AZURE_OPENAI_EMBEDDING_API_KEY: str = os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY', '')
    AZURE_OPENAI_EMBEDDING_ENDPOINT: str = os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT', '')