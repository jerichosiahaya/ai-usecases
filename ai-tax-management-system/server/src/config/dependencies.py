from functools import lru_cache
from typing import Annotated, Optional
from fastapi import Depends
from loguru import logger

from src.config.env import AppConfig
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.messaging import RabbitMQRepository, AzureServiceBusRepository
from src.repository.storage import MinioStorageRepository, AzureBlobStorageRepository
from src.repository.database import AzureCosmosDBRepository
from src.usecase.content_extraction import ContentExtraction
from src.usecase.file_upload import FileUpload
from src.usecase.gl_upload import GLUpload
from src.usecase.tax_management import TaxManagementUseCase
from src.repository.llm.llm_service import LLMService

# Module-level singleton instances
_content_understanding_repo: Optional[ContentUnderstandingRepository] = None
_azure_blob_storage_repo: Optional[AzureBlobStorageRepository] = None
_azure_cosmos_repo: Optional[AzureCosmosDBRepository] = None
_rabbitmq_repo: Optional[RabbitMQRepository] = None
_minio_storage_repo: Optional[MinioStorageRepository] = None
_azure_service_bus_repo: Optional[AzureServiceBusRepository] = None
_llm_service_repo: Optional[LLMService] = None


@lru_cache
def get_app_config() -> AppConfig:
    """
    Get application configuration (cached singleton).
    
    Returns:
        AppConfig instance with environment variables
    """
    logger.info("Initializing application configuration")
    return AppConfig()


def get_content_understanding_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> ContentUnderstandingRepository:
    """
    Create and return ContentUnderstandingRepository instance (singleton).
    
    This repository wraps Azure AI Document Intelligence client which is expensive
    to create and maintains internal connection pooling. Creating once at startup
    and reusing across requests is the recommended approach.
    
    Args:
        config: Application configuration dependency
        
    Returns:
        ContentUnderstandingRepository singleton instance
    """
    global _content_understanding_repo
    if _content_understanding_repo is None:
        logger.info("Creating ContentUnderstandingRepository singleton")
        _content_understanding_repo = ContentUnderstandingRepository(config=config)
    return _content_understanding_repo


def get_azure_blob_storage_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> AzureBlobStorageRepository:
    """
    Create and return AzureBlobStorageRepository instance (singleton).
    
    This repository wraps Azure Blob Storage client which is thread-safe and
    maintains internal connection pooling. Creating once at startup and reusing
    across requests is the recommended approach.
    
    Args:
        config: Application configuration dependency
        
    Returns:
        BlobStorageRepository singleton instance
    """
    global _azure_blob_storage_repo
    if _azure_blob_storage_repo is None:
        logger.info("Creating AzureBlobStorageRepository singleton")
        _azure_blob_storage_repo = AzureBlobStorageRepository(
            connection_string=config.AZURE_STORAGE_CONNECTION_STRING,
            container_name="tax-documents"
        )
    return _azure_blob_storage_repo


def get_azure_cosmos_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> Optional[AzureCosmosDBRepository]:
    """
    Create and return AzureCosmosDBRepository instance (singleton).
    
    Cosmos DB client is thread-safe and maintains internal connection pooling.
    
    Args:
        config: Application configuration dependency
        
    Returns:
        AzureCosmosDBRepository singleton instance or None if not configured
    """
    global _azure_cosmos_repo
    if _azure_cosmos_repo is None and config.COSMOSDB_CONNECTION_STRING:
        logger.info("Creating AzureCosmosDBRepository singleton")
        try:
            _azure_cosmos_repo = AzureCosmosDBRepository(
                connection_string=config.COSMOSDB_CONNECTION_STRING,
                database_id=config.COSMOSDB_DATABASE,
                container_id=config.COSMOSDB_CONTAINER
            )
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB repository: {e}")
            return None
    return _azure_cosmos_repo


def get_rabbitmq_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> Optional[RabbitMQRepository]:
    """
    Create and return RabbitMQRepository instance (singleton).
    
    RabbitMQ client maintains connection pooling and should be reused.
    Only initialized in development environment. Returns None in production.
    
    Args:
        config: Application configuration dependency
        
    Returns:
        RabbitMQRepository singleton instance or None if not initialized
    """
    global _rabbitmq_repo
    # In production, this will remain None if not initialized at startup
    if _rabbitmq_repo is None and config.ENV.lower() == "development":
        logger.info("Creating RabbitMQRepository singleton")
        _rabbitmq_repo = RabbitMQRepository(
            host="localhost",
            port=5672,
            username=config.RABBITMQ_DEFAULT_USER,
            password=config.RABBITMQ_DEFAULT_PASS
        )
    return _rabbitmq_repo


def get_minio_storage_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> Optional[MinioStorageRepository]:
    """
    Create and return MinioStorageRepository instance (singleton).
    
    MinIO client is thread-safe and maintains internal connection pooling.
    Only initialized in development environment. Returns None in production.
    
    Args:
        config: Application configuration dependency
        
    Returns:
        MinioStorageRepository singleton instance or None if not initialized
    """
    global _minio_storage_repo
    # In production, this will remain None if not initialized at startup
    if _minio_storage_repo is None and config.ENV.lower() == "development":
        logger.info("Creating MinioStorageRepository singleton")
        _minio_storage_repo = MinioStorageRepository(
            endpoint="localhost:9100",
            access_key=config.MINIO_ROOT_USER,
            secret_key=config.MINIO_ROOT_PASSWORD,
            bucket_name="tax-documents",
            secure=False
        )
    return _minio_storage_repo

def get_azure_service_bus_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> Optional[AzureServiceBusRepository]:
    """
    Create and return AzureServiceBusRepository instance (singleton).
    
    Service Bus client is thread-safe and maintains internal connection pooling.
    
    Args:
        config: Application configuration dependency
    Returns:
        AzureServiceBusRepository singleton instance or None if not configured
    """
    if not config.AZURE_SERVICE_BUS_CONNECTION_STRING:
        return None
    logger.info("Creating AzureServiceBusRepository singleton")
    return AzureServiceBusRepository(
        connection_string=config.AZURE_SERVICE_BUS_CONNECTION_STRING
    )

def get_llm_service_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> Optional[LLMService]:
    """
    Create and return LLMService instance (singleton).
    
    LLMService wraps Azure OpenAI client which is thread-safe and
    maintains internal connection pooling. Creating once at startup
    and reusing across requests is the recommended approach.
    
    Args:
        config: Application configuration dependency
    Returns:
        LLMService singleton instance
    """
    global _llm_service_repo
    if _llm_service_repo is None:
        logger.info("Creating LLMService singleton")
        _llm_service_repo = LLMService(
            service_id="default_service",
            config=config
        )
    return _llm_service_repo

def get_content_extraction_service(
    content_understanding_repo: Annotated[
        ContentUnderstandingRepository, 
        Depends(get_content_understanding_repository)
    ],
    blob_storage_repo: Annotated[
        AzureBlobStorageRepository, 
        Depends(get_azure_blob_storage_repository)
    ],
    rabbitmq_repo: Annotated[
        Optional[RabbitMQRepository],
        Depends(get_rabbitmq_repository)
    ],
    minio_storage_repo: Annotated[
        Optional[MinioStorageRepository],
        Depends(get_minio_storage_repository)
    ],
    llm_service_repo: Annotated[
        Optional[LLMService],
        Depends(get_llm_service_repository)
    ],
    azure_cosmos_repo: Annotated[
        Optional[AzureCosmosDBRepository],
        Depends(get_azure_cosmos_repository)
    ]

) -> ContentExtraction:
    """
    Create and return ContentExtraction use case with all dependencies.
    
    RabbitMQ and MinIO are optional and only available in development environment.
    In production, they will be None and Azure services will be used instead.
    
    Args:
        content_understanding_repo: Content Understanding repository dependency
        blob_storage_repo: Blob Storage repository dependency
        rabbitmq_repo: Optional RabbitMQ repository (development only)
        minio_storage_repo: Optional MinIO storage repository (development only)
        
    Returns:
        ContentExtraction use case instance
    """
    logger.debug("Creating ContentExtraction use case")
    return ContentExtraction(
        content_understanding_repo=content_understanding_repo,
        azure_blob_storage_repo=blob_storage_repo,
        rabbitmq_repo=rabbitmq_repo,
        minio_storage_repo=minio_storage_repo,
        llm_service_repo=llm_service_repo,
        azure_cosmos_repo=azure_cosmos_repo
    )

def get_file_upload_service(
    content_understanding_repo: Annotated[
        ContentUnderstandingRepository, 
        Depends(get_content_understanding_repository)
    ],
    azure_blob_storage_repo: Annotated[
        AzureBlobStorageRepository, 
        Depends(get_azure_blob_storage_repository)
    ],
    azure_cosmos_repo: Annotated[
        Optional[AzureCosmosDBRepository],
        Depends(get_azure_cosmos_repository)
    ],
    rabbitmq_repo: Annotated[
        Optional[RabbitMQRepository],
        Depends(get_rabbitmq_repository)
    ],
    minio_storage_repo: Annotated[
        Optional[MinioStorageRepository],
        Depends(get_minio_storage_repository)
    ],
    azure_service_bus_repo: Annotated[
        Optional[AzureServiceBusRepository],
        Depends(get_azure_service_bus_repository)
    ]
) -> FileUpload:
    logger.debug("Creating FileUpload use case")
    return FileUpload(
        content_understanding_repo=content_understanding_repo,
        azure_blob_storage_repo=azure_blob_storage_repo,
        azure_cosmos_repo=azure_cosmos_repo,
        rabbitmq_repo=rabbitmq_repo,
        minio_storage_repo=minio_storage_repo,
        azure_service_bus_repo=azure_service_bus_repo
    )

def get_gl_upload_service(
    content_understanding_repo: Annotated[
        ContentUnderstandingRepository, 
        Depends(get_content_understanding_repository)
    ],
    azure_blob_storage_repo: Annotated[
        AzureBlobStorageRepository, 
        Depends(get_azure_blob_storage_repository)
    ],
    azure_cosmos_repo: Annotated[
        Optional[AzureCosmosDBRepository],
        Depends(get_azure_cosmos_repository)
    ],
    rabbitmq_repo: Annotated[
        Optional[RabbitMQRepository],
        Depends(get_rabbitmq_repository)
    ],
    minio_storage_repo: Annotated[
        Optional[MinioStorageRepository],
        Depends(get_minio_storage_repository)
    ],
    azure_service_bus_repo: Annotated[
        Optional[AzureServiceBusRepository],
        Depends(get_azure_service_bus_repository)
    ]
) -> GLUpload:
    logger.debug("Creating GLUpload use case")
    return GLUpload(
        content_understanding_repo=content_understanding_repo,
        azure_blob_storage_repo=azure_blob_storage_repo,
        azure_cosmos_repo=azure_cosmos_repo,
        rabbitmq_repo=rabbitmq_repo,
        minio_storage_repo=minio_storage_repo,
        azure_service_bus_repo=azure_service_bus_repo
    )

def get_tax_management_service(
    azure_cosmos_repo: Annotated[
        Optional[AzureCosmosDBRepository],
        Depends(get_azure_cosmos_repository)
    ]
) -> TaxManagementUseCase:
    return TaxManagementUseCase(
        azure_cosmos_repo=azure_cosmos_repo
    )

TaxManagementDep = Annotated[TaxManagementUseCase, Depends(get_tax_management_service)]
ContentExtractionDep = Annotated[ContentExtraction, Depends(get_content_extraction_service)]
FileUploadDep = Annotated[FileUpload, Depends(get_file_upload_service)]
GLUploadDep = Annotated[GLUpload, Depends(get_gl_upload_service)]
AzureCosmosRepoDep = Annotated[Optional[AzureCosmosDBRepository], Depends(get_azure_cosmos_repository)]
RabbitMQDep = Annotated[Optional[RabbitMQRepository], Depends(get_rabbitmq_repository)]
MinioStorageDep = Annotated[Optional[MinioStorageRepository], Depends(get_minio_storage_repository)]
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
