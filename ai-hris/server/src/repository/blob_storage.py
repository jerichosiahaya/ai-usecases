from azure.storage.blob import BlobServiceClient, ContainerClient
from loguru import logger
import uuid
from datetime import datetime


class BlobStorageRepository:
    def __init__(self, connection_string: str, container_name: str = "hris"):
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

    def upload_file(self, file, candidate_id: str, original_filename: str) -> dict:
        """
        Upload a file to Blob Storage organized by candidate ID
        
        Args:
            file: File object from Flask request
            candidate_id: ID of the candidate to organize files
            original_filename: Original name of the file
            
        Returns:
            Dictionary with file metadata including blob URL
        """
        try:
            # Generate unique blob name with candidate_id folder structure
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
            unique_filename = f"{uuid.uuid4()}.{original_filename}.{file_extension}" if file_extension else str(uuid.uuid4())
            blob_name = f"{candidate_id}/{unique_filename}"
            
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
                "candidate_id": candidate_id,
                "size": blob_properties.size,
                "content_type": getattr(file, 'content_type', 'application/octet-stream'),
                "uploaded_at": datetime.utcnow().isoformat(),
                "url": blob_client.url
            }
            
            logger.info(f"Uploaded file {original_filename} for candidate {candidate_id}, blob: {blob_name}")
            return file_info
        
        except Exception as e:
            logger.error(f"Error uploading file for candidate {candidate_id}: {e}")
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

    def list_files(self, candidate_id: str) -> list:
        """List all files for a specific candidate"""
        try:
            prefix = f"candidates/{candidate_id}/documents/"
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            files = []
            for blob in blobs:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                files.append({
                    "blob_name": blob.name,
                    "original_filename": blob.name.split('/')[-1],
                    "size": blob.size,
                    "created_at": blob.creation_time.isoformat() if blob.creation_time else None,
                    "url": blob_client.url
                })
            logger.info(f"Listed {len(files)} files for candidate {candidate_id}")
            return files
        except Exception as e:
            logger.error(f"Error listing files for candidate {candidate_id}: {e}")
            raise

    def delete_candidate_documents(self, candidate_id: str) -> int:
        """Delete all documents for a specific candidate"""
        try:
            prefix = f"candidates/{candidate_id}/documents/"
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            count = 0
            
            for blob in blobs:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=blob.name
                )
                blob_client.delete_blob()
                count += 1
            
            logger.info(f"Deleted {count} documents for candidate {candidate_id}")
            return count
        except Exception as e:
            logger.error(f"Error deleting documents for candidate {candidate_id}: {e}")
            raise
