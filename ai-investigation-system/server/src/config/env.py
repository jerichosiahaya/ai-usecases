import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppConfig:
    # Azure OpenAI Configuration
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', '')
    AZURE_OPENAI_API_BASE: str = os.getenv('AZURE_OPENAI_API_BASE', '')
    AZURE_OPENAI_API_VERSION: str = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    AZURE_OPENAI_API_KEY: str = os.getenv('AZURE_OPENAI_API_KEY', '')

    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-3-small')

    # SQL Server Configuration
    SQL_SERVER_CONNECTION_STRING: str = os.getenv('SQL_SERVER_CONNECTION_STRING', '')
    
    # Cosmos DB Configuration
    COSMOS_DB_CONNECTION_STRING: str = os.getenv('COSMOS_DB_CONNECTION_STRING', '')
    
    # Azure Blob Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
    
    # Azure Service Bus Configuration
    SERVICE_BUS_CONNECTION_STRING: str = os.getenv('SERVICE_BUS_CONNECTION_STRING', '')
    SERVICE_BUS_QUEUE_NAME: str = os.getenv('SERVICE_BUS_QUEUE_NAME', 'fraud-processing-queue')