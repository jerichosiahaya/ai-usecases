from typing import Dict, Any, Optional
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.storage import MinioStorageRepository, AzureBlobStorageRepository
from src.repository.messaging import RabbitMQRepository
from loguru import logger
from src.domain.file_upload import FileUploadResponse
from src.common.const import Environment

import os
IS_PRODUCTION = os.getenv("ENV") == Environment.Production.value

class FileUpload:
    def __init__(
        self, 
        content_understanding_repo: ContentUnderstandingRepository,
        azure_blob_storage_repo: AzureBlobStorageRepository,
        rabbitmq_repo: Optional[RabbitMQRepository] = None,
        minio_storage_repo: Optional[MinioStorageRepository] = None
    ):
        """
        Initialize the content extraction usecase
        
        Args:
            content_understanding_repo: Repository for Azure AI Content Understanding API
            azure_blob_storage_repo: Repository for Azure Blob Storage
            rabbitmq_repo: Optional RabbitMQ repository for messaging (development only)
            minio_storage_repo: Optional MinIO repository for object storage (development only)
        """
        self.content_understanding_repo = content_understanding_repo
        self.azure_blob_storage_repo = azure_blob_storage_repo
        self.rabbitmq_repo = rabbitmq_repo
        self.minio_storage_repo = minio_storage_repo

    def upload(self, file, file_id: str, original_filename: str, activity_id: str = None) -> Dict[str, Any]:
        """
        Extract content from a document by uploading to blob storage and analyzing with Content Understanding API
        
        Args:
            file: File object to extract content from
            file_id: ID of the case to associate with the file
            original_filename: Original name of the file
            
        Returns:
            Dictionary containing the analysis results
            
        Raises:
            Exception: If upload or analysis fails
        """
        try:
            if IS_PRODUCTION:
                file_info = self.azure_blob_storage_repo.upload_file(
                    file=file, 
                    file_id=file_id, 
                    original_filename=original_filename,
                    activity_id=activity_id
                )
            else:
                file_info = self.minio_storage_repo.upload_file(
                    file=file, 
                    file_id=file_id, 
                    original_filename=original_filename,
                    activity_id=activity_id
                )

                messaging_payload = {
                    "file_id": file_id,
                    "blob_name": file_info["object_name"],
                    "original_filename": original_filename
                }
                self.rabbitmq_repo.send_message(
                    queue_name="file_upload_queue",
                    message_data=messaging_payload
                )

            return FileUploadResponse(
                file_id=file_id,
                activity_id=activity_id,
                file_name=original_filename,
                file_size=file_info.get("size", 0),
                content_type=file_info.get("content_type"),
                status="processing"
            )
        
        except Exception as e:
            logger.error(f"Error extracting content from {original_filename}: {e}")
            raise