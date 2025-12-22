from typing import Dict, Any, Optional, List, BinaryIO
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.storage import MinioStorageRepository, AzureBlobStorageRepository
from src.repository.messaging import RabbitMQRepository
from src.repository.database import AzureCosmosDBRepository
from loguru import logger
from src.domain.file_upload import FileUploadResponse
from src.common.const import Environment
from pypdf import PdfReader, PdfWriter
from io import BytesIO
from datetime import datetime

import os
IS_PRODUCTION = os.getenv("ENV") == Environment.Production.value

class FileUpload:
    def __init__(
        self, 
        content_understanding_repo: ContentUnderstandingRepository,
        azure_blob_storage_repo: AzureBlobStorageRepository,
        azure_cosmos_repo: Optional[AzureCosmosDBRepository] = None,
        rabbitmq_repo: Optional[RabbitMQRepository] = None,
        minio_storage_repo: Optional[MinioStorageRepository] = None
    ):
        """
        Initialize the file upload usecase
        
        Args:
            content_understanding_repo: Repository for Azure AI Content Understanding API
            azure_blob_storage_repo: Repository for Azure Blob Storage
            azure_cosmos_repo: Repository for Cosmos DB to store upload metadata
            rabbitmq_repo: Optional RabbitMQ repository for messaging (development only)
            minio_storage_repo: Optional MinIO repository for object storage (development only)
        """
        self.content_understanding_repo = content_understanding_repo
        self.azure_blob_storage_repo = azure_blob_storage_repo
        self.azure_cosmos_repo = azure_cosmos_repo
        self.rabbitmq_repo = rabbitmq_repo
        self.minio_storage_repo = minio_storage_repo

    def _upload_to_storage(
        self, 
        file: BinaryIO, 
        file_id: str, 
        filename: str, 
        activity_id: str
    ) -> Dict[str, Any]:
        """
        Upload a file to the appropriate storage (Azure or MinIO based on environment)
        
        Args:
            file: File-like object to upload
            file_id: Unique file identifier
            filename: Name of the file
            activity_id: Activity ID to group related files
            
        Returns:
            Dictionary containing upload metadata
        """
        storage_repo = self.azure_blob_storage_repo if IS_PRODUCTION else self.minio_storage_repo
        return storage_repo.upload_file(
            file=file,
            file_id=file_id,
            original_filename=filename,
            activity_id=activity_id
        )
    
    def _send_processing_message(
        self, 
        file_id: str, 
        object_name: str, 
        filename: str, 
        page_number: Optional[int] = None
    ) -> None:
        """
        Send a message to RabbitMQ for file processing (development only)
        
        Args:
            file_id: Unique file identifier
            object_name: Storage object name/path
            filename: Original filename
            page_number: Optional page number for multi-page PDFs
        """
        if IS_PRODUCTION or not self.rabbitmq_repo:
            return
            
        payload = {
            "file_id": file_id,
            "blob_name": object_name,
            "original_filename": filename
        }
        
        if page_number is not None:
            payload["page_number"] = page_number
            
        self.rabbitmq_repo.send_message(
            queue_name="file_upload_queue",
            message_data=payload
        )

    def _split_pdf_pages(self, file_content: bytes, original_filename: str) -> List[tuple]:
        """
        Split a PDF file into individual pages
        
        Args:
            file_content: PDF file content as bytes
            original_filename: Original PDF filename
            
        Returns:
            List of tuples containing (page_number, page_content_bytes, page_filename)
        """
        reader = PdfReader(BytesIO(file_content))
        total_pages = len(reader.pages)
        
        logger.info(f"Splitting PDF {original_filename} into {total_pages} pages")
        
        pages = []
        base_filename = original_filename.rsplit('.', 1)[0]
        
        for page_num in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])
            
            page_buffer = BytesIO()
            writer.write(page_buffer)
            page_buffer.seek(0)
            
            page_filename = f"{base_filename}_page_{page_num + 1}.pdf"
            pages.append((page_num + 1, page_buffer.read(), page_filename))
            
        logger.info(f"Successfully split {original_filename} into {len(pages)} pages")
        return pages

    def _upload_single_file(
        self, 
        file_content: bytes, 
        file_id: str, 
        filename: str, 
        activity_id: str,
        page_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Upload a single file and send processing message
        
        Args:
            file_content: File content as bytes
            file_id: Unique file identifier
            filename: Name of the file
            activity_id: Activity ID to group related files
            page_number: Optional page number for PDF pages
            
        Returns:
            Dictionary containing file metadata
        """
        file_buffer = BytesIO(file_content)
        file_info = self._upload_to_storage(file_buffer, file_id, filename, activity_id)
        
        object_name = file_info.get("object_name") or file_info.get("blob_name")
        self._send_processing_message(file_id, object_name, filename, page_number)
        
        result = {
            "filename": filename,
            "size": file_info.get("size", 0),
            "object_name": object_name
        }
        
        if page_number is not None:
            result["page"] = page_number
            
        return result

    def upload(self, file, file_id: str, original_filename: str, activity_id: str = None) -> Dict[str, Any]:
        """
        Upload a document file, splitting multi-page PDFs into individual pages
        
        For PDF files with multiple pages, each page will be split and uploaded as a separate file
        to the same folder (activity_id). All files are uploaded to Azure Blob Storage (production)
        or MinIO (development).
        
        Args:
            file: File object to upload
            file_id: Unique file identifier
            original_filename: Original name of the file
            activity_id: Activity ID to group related files
            
        Returns:
            Dictionary containing upload results and file metadata
            
        Raises:
            Exception: If upload or processing fails
        """
        try:
            file_content = file.read()
            is_pdf = original_filename.lower().endswith('.pdf')
            uploaded_files = []
            
            # Try to split PDF into pages
            if is_pdf:
                try:
                    pages = self._split_pdf_pages(file_content, original_filename)
                    logger.info(f"Uploading {len(pages)} pages from PDF {original_filename}")
                    
                    for page_num, page_content, page_filename in pages:
                        file_info = self._upload_single_file(
                            file_content=page_content,
                            file_id=file_id,
                            filename=page_filename,
                            activity_id=activity_id,
                            page_number=page_num
                        )
                        uploaded_files.append(file_info)
                        
                except Exception as pdf_error:
                    logger.warning(f"Failed to split PDF, uploading as single file: {pdf_error}")
                    is_pdf = False
            
            # Upload as single file (non-PDF or failed split)
            if not uploaded_files:
                file_info = self._upload_single_file(
                    file_content=file_content,
                    file_id=file_id,
                    filename=original_filename,
                    activity_id=activity_id
                )
                uploaded_files.append(file_info)

            total_size = sum(f["size"] for f in uploaded_files)
            
            upload_result = {
                "file_id": file_id,
                "activity_id": activity_id,
                "original_filename": original_filename,
                "total_size": total_size,
                "total_pages": len(uploaded_files) if is_pdf and len(uploaded_files) > 1 else 1,
                "uploaded_files": uploaded_files,
                "status": "processing"
            }
            
            # Store upload metadata in Cosmos DB if repository is available
            if self.azure_cosmos_repo:
                try:
                    cosmos_document = {
                        "id": file_id,
                        "activity_id": activity_id,
                        "original_filename": original_filename,
                        "total_size": total_size,
                        "total_pages": len(uploaded_files) if is_pdf and len(uploaded_files) > 1 else 1,
                        "is_multi_page": len(uploaded_files) > 1,
                        "files": uploaded_files,
                        "status": "pending",
                        "uploaded_at": datetime.utcnow().isoformat()
                    }
                    
                    self.azure_cosmos_repo.create_document(
                        document_data=cosmos_document,
                        document_type="upload",
                        partition_key=activity_id
                    )
                    logger.info(f"Stored upload metadata in Cosmos DB for file_id: {file_id}")
                except Exception as cosmos_error:
                    logger.error(f"Failed to store upload metadata in Cosmos DB: {cosmos_error}")
                    # Don't fail the upload if Cosmos DB insert fails
            
            return upload_result
        
        except Exception as e:
            logger.error(f"Error uploading file {original_filename}: {e}")
            raise

    def get_status(self, document_id: str):
        
        try:
            document = self.azure_cosmos_repo.query_documents(
                container_id="uploads",
                query_filter=f"c.documentId = '{document_id}'",
                max_items=1
            )
            if not document:
                raise Exception(f"No upload found with document ID: {document_id}")
            
            return document[0]
            
        except Exception as e:
            logger.error(f"Error retrieving status for document ID {document_id}: {e}")
            raise