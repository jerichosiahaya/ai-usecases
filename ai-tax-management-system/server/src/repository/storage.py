from azure.storage.blob import BlobServiceClient, ContainerClient
from minio import Minio
from loguru import logger
import uuid
from datetime import datetime
from io import BytesIO

class AzureBlobStorageRepository:
    def __init__(self, connection_string: str, container_name: str):
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

    def upload_file(self, file, file_id: str, original_filename: str, activity_id: str, content_type: str = None) -> dict:
        """
        Upload a file to Blob Storage
        
        Args:
            file: File object from Flask request or BytesIO
            file_id: ID of the case to associate with the file
            original_filename: Original name of the file
            activity_id: Activity ID to group related files
            content_type: MIME type of the file (optional)
            
        Returns:
            Dictionary with file metadata
        """
        try:
            file_name = original_filename.split('.')[0] if '.' in original_filename else original_filename
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
            object_name = f"{file_id}/{file_name}.{file_extension}"
            
            # Upload file
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=object_name
            )
            
            file_content = file.read()
            blob_client.upload_blob(file_content, overwrite=True)
            
            # Get blob properties
            blob_properties = blob_client.get_blob_properties()
            
            # Use provided content_type or get from file object
            if content_type is None:
                content_type = getattr(file, 'content_type', 'application/octet-stream')
            
            file_info = {
                "blob_name": object_name,
                "original_filename": original_filename,
                "file_id": file_id,
                "size": blob_properties.size,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "url": blob_client.url
            }
            
            logger.info(f"Uploaded file {original_filename} for case {file_id}, blob: {object_name}")
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

    def list_files(self, file_id: str) -> list:
        """List all files for a specific case"""
        try:
            blobs = self.container_client.list_blobs(name_starts_with=f"{file_id}/")
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
            logger.info(f"Listed {len(files)} files for case {file_id}")
            return files
        except Exception as e:
            logger.error(f"Error listing files for case {file_id}: {e}")
            raise

class MinioStorageRepository:
    """
    Simple MinIO object storage repository for file operations.
    """
    
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str, secure: bool = False):
        """
        Initialize MinIO client.
        
        Args:
            endpoint: MinIO server endpoint (e.g., 'localhost:9000')
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket_name: Bucket name to use
            secure: Use HTTPS (True) or HTTP (False)
        """
        try:
            self.client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )
            self.bucket_name = bucket_name
            self.endpoint = endpoint
            self.secure = secure
            
            # Create bucket if it doesn't exist
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {bucket_name}")
            
            logger.info(f"Connected to MinIO at {endpoint}, bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MinIO: {e}")
            raise

    def upload_file(self, file, file_id: str, original_filename: str, activity_id: str, content_type: str = None) -> dict:
        """
        Upload a file to MinIO
        
        Args:
            file: File object to upload
            file_id: ID of the case to associate with the file
            original_filename: Original name of the file
            activity_id: Activity ID to group related files
            content_type: MIME type of the file (optional)
            
        Returns:
            Dictionary with file metadata
        """
        try:
            # Generate unique object name
            file_name = original_filename.split('.')[0] if '.' in original_filename else original_filename
            file_extension = original_filename.split('.')[-1] if '.' in original_filename else ''
            object_name = f"{activity_id}/{file_id}/{file_name}.{file_extension}"
            
            # Read file content
            file_content = file.read()
            file_size = len(file_content)
            
            # Use provided content_type or get from file object
            if content_type is None:
                content_type = getattr(file, 'content_type', 'application/octet-stream')
            
            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=BytesIO(file_content),
                length=file_size,
                content_type=content_type
            )
            
            # Construct URL based on secure flag
            protocol = "https" if self.secure else "http"
            url = f"{protocol}://{self.endpoint}/{self.bucket_name}/{object_name}"
            
            file_info = {
                "object_name": object_name,
                "original_filename": original_filename,
                "file_id": file_id,
                "size": file_size,
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "url": url
            }
            
            logger.info(f"Uploaded file {original_filename} for case {file_id}, object: {object_name}")
            return file_info
        
        except Exception as e:
            logger.error(f"Error uploading file to MinIO: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """Delete a file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            logger.info(f"Deleted object: {object_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting object {object_name}: {e}")
            raise
    
    def get_file_url(self, object_name: str) -> str:
        """Get the URL of an object"""
        try:
            protocol = "https" if self.secure else "http"
            return f"{protocol}://{self.endpoint}/{self.bucket_name}/{object_name}"
        except Exception as e:
            logger.error(f"Error getting file URL: {e}")
            raise
    
    def list_files(self, file_id: str) -> list:
        """List all files for a specific case"""
        try:
            protocol = "https" if self.secure else "http"
            objects = self.client.list_objects(self.bucket_name, prefix=f"{file_id}/")
            files = []
            for obj in objects:
                files.append({
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "created_at": obj.last_modified.isoformat() if obj.last_modified else None,
                    "url": f"{protocol}://{self.endpoint}/{self.bucket_name}/{obj.object_name}"
                })
            logger.info(f"Listed {len(files)} files for case {file_id}")
            return files
        except Exception as e:
            logger.error(f"Error listing files for case {file_id}: {e}")
            raise
