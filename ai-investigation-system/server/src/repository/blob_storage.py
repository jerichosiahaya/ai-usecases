from azure.storage.blob import BlobServiceClient, ContainerClient
from loguru import logger
import uuid
from datetime import datetime


class BlobStorageRepository:
    def __init__(self, connection_string: str, container_name: str = "ai-fraud"):
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            self.container_name = container_name
            
            # Get or create container
            self.container_client = self.blob_service_client.get_container_client(container_name)
            try:
                self.container_client.create_container()
                logger.info(f"Created blob container: {container_name}")
            except Exception as e:
                if "ContainerAlreadyExists" in str(e):
                    logger.info(f"Blob container already exists: {container_name}")
                else:
                    raise
            
            logger.info(f"Connected to Blob Storage, container: {container_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Blob Storage: {e}")
            raise

    def upload_file(self, file, case_id: str, original_filename: str) -> dict:
        """
        Upload a file to Blob Storage
        
        Args:
            file: File object from Flask request
            case_id: ID of the case to associate with the file
            original_filename: Original name of the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            # Generate unique blob name
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
            blob_name = f"{case_id}/{uuid.uuid4()}.{file_extension}"
            
            # Upload file
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            file_content = file.read()
            blob_client.upload_blob(file_content, overwrite=True)
            
            # Get blob properties
            blob_properties = blob_client.get_blob_properties()
            
            file_info = {
                "blob_name": blob_name,
                "original_filename": original_filename,
                "case_id": case_id,
                "size": blob_properties.size,
                "content_type": file.content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "url": blob_client.url
            }
            
            logger.info(f"Uploaded file {original_filename} for case {case_id}, blob: {blob_name}")
            return file_info
        
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise

    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from Blob Storage"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting blob {blob_name}: {e}")
            raise

    def get_file_url(self, blob_name: str) -> str:
        """Get the URL of a blob"""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            return blob_client.url
        except Exception as e:
            logger.error(f"Error getting file URL: {e}")
            raise

    def list_files(self, case_id: str) -> list:
        """List all files for a specific case"""
        try:
            blobs = self.container_client.list_blobs(name_starts_with=f"{case_id}/")
            files = []
            for blob in blobs:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                files.append({
                    "blob_name": blob.name,
                    "size": blob.size,
                    "created_at": blob.creation_time.isoformat() if blob.creation_time else None,
                    "url": blob_client.url
                })
            logger.info(f"Listed {len(files)} files for case {case_id}")
            return files
        except Exception as e:
            logger.error(f"Error listing files for case {case_id}: {e}")
            raise
