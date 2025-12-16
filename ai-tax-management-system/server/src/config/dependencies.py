"""
Dependency injection container for FastAPI routes.

This module provides dependency functions that initialize and inject
repositories and use cases into route handlers.
"""

from functools import lru_cache
from typing import Annotated, Optional
from fastapi import Depends
from loguru import logger

from src.config.env import AppConfig
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.blob_storage import BlobStorageRepository
from src.usecase.content_extraction import ContentExtraction


# Module-level singleton instances
_content_understanding_repo: Optional[ContentUnderstandingRepository] = None
_blob_storage_repo: Optional[BlobStorageRepository] = None


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


def get_blob_storage_repository(
    config: Annotated[AppConfig, Depends(get_app_config)]
) -> BlobStorageRepository:
    """
    Create and return BlobStorageRepository instance (singleton).
    
    This repository wraps Azure Blob Storage client which is thread-safe and
    maintains internal connection pooling. Creating once at startup and reusing
    across requests is the recommended approach.
    
    Args:
        config: Application configuration dependency
        
    Returns:
        BlobStorageRepository singleton instance
    """
    global _blob_storage_repo
    if _blob_storage_repo is None:
        logger.info("Creating BlobStorageRepository singleton")
        _blob_storage_repo = BlobStorageRepository(
            connection_string=config.AZURE_STORAGE_CONNECTION_STRING,
            container_name="tax-documents"
        )
    return _blob_storage_repo


def get_content_extraction_service(
    content_understanding_repo: Annotated[
        ContentUnderstandingRepository, 
        Depends(get_content_understanding_repository)
    ],
    blob_storage_repo: Annotated[
        BlobStorageRepository, 
        Depends(get_blob_storage_repository)
    ]
) -> ContentExtraction:
    """
    Create and return ContentExtraction use case with all dependencies.
    
    Args:
        content_understanding_repo: Content Understanding repository dependency
        blob_storage_repo: Blob Storage repository dependency
        
    Returns:
        ContentExtraction use case instance
    """
    logger.debug("Creating ContentExtraction use case")
    return ContentExtraction(
        content_understanding_repo=content_understanding_repo,
        blob_storage_repo=blob_storage_repo
    )


# Type aliases for cleaner route signatures
ContentExtractionDep = Annotated[ContentExtraction, Depends(get_content_extraction_service)]
AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
