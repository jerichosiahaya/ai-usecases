from typing import Dict, Any, Optional, List, BinaryIO
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.storage import MinioStorageRepository, AzureBlobStorageRepository
from src.repository.messaging import RabbitMQRepository, AzureServiceBusRepository
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
        minio_storage_repo: Optional[MinioStorageRepository] = None,
        azure_service_bus_repo: Optional[AzureServiceBusRepository] = None
    ):
        self.content_understanding_repo = content_understanding_repo
        self.azure_blob_storage_repo = azure_blob_storage_repo
        self.azure_cosmos_repo = azure_cosmos_repo
        self.rabbitmq_repo = rabbitmq_repo
        self.minio_storage_repo = minio_storage_repo
        self.azure_service_bus_repo = azure_service_bus_repo

        self.queue_name = "document-uploads"

    def _upload_to_storage(
        self, 
        file: BinaryIO, 
        file_id: str, 
        filename: str, 
        activity_id: str,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        
        storage_repo = self.azure_blob_storage_repo if IS_PRODUCTION else self.minio_storage_repo
        return storage_repo.upload_file(
            file=file,
            file_id=file_id,
            original_filename=filename,
            activity_id=activity_id,
            content_type=content_type
        )
    
    def _send_processing_message(
        self, 
        file_id: str
    ) -> None:

        # if IS_PRODUCTION or not self.rabbitmq_repo:
        #     return
            
        payload = {
            "document_id": file_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # self.rabbitmq_repo.send_message(
        #     queue_name="file_upload_queue",
        #     message_data=payload
        # )

        self.azure_service_bus_repo.send_message(
            queue_name=self.queue_name,
            message_data=payload
        )

    def _split_pdf_pages(self, file_content: bytes, original_filename: str) -> List[tuple]:

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
            
            page_filename = f"{base_filename}_{page_num + 1}.pdf"
            pages.append((page_num + 1, page_buffer.read(), page_filename))
            
        logger.info(f"Successfully split {original_filename} into {len(pages)} pages")
        return pages

    def _upload_single_file(
        self, 
        file_content: bytes, 
        file_id: str, 
        filename: str, 
        activity_id: str,
        page_number: Optional[int] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:

        file_buffer = BytesIO(file_content)
        file_info = self._upload_to_storage(file_buffer, file_id, filename, activity_id, content_type)
        
        object_name = file_info.get("object_name") or file_info.get("blob_name")
        # self._send_processing_message(file_id, object_name, filename, page_number)
        
        result = {
            "filename": filename,
            "size": file_info.get("size", 0),
            "object_name": object_name
        }
        
        if page_number is not None:
            result["page"] = page_number
            
        return result

    def upload(self, file, file_id: str, original_filename: str, activity_id: str = None) -> Dict[str, Any]:
        
        try:
            file_content = file.read()
            is_pdf = original_filename.lower().endswith('.pdf')
            uploaded_files = []
            # Extract content_type from original file object
            content_type = getattr(file, 'content_type', 'application/octet-stream')
            
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
                            page_number=page_num,
                            content_type='application/pdf'
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
                    activity_id=activity_id,
                    content_type=content_type
                )
                uploaded_files.append(file_info)

            total_size = sum(f["size"] for f in uploaded_files)
            
            upload_result = {
                "id": file_id,
                "documentId": file_id,
                "originalFilename": original_filename,
                "totalSize": total_size,
                "totalPages": len(uploaded_files) if is_pdf and len(uploaded_files) > 1 else 1,
                "uploadedFiles": uploaded_files,
                "status": "processing"
            }

            # Store upload metadata in database
            self.azure_cosmos_repo.create_document(
                container_id="uploads",
                document_data=upload_result
            )
            
            self._send_processing_message(file_id)
            
            # Return as snake_case
            return {
                "document_id": upload_result["documentId"],
                "original_filename": upload_result["originalFilename"],
                "total_size": upload_result["totalSize"],
                "total_pages": upload_result["totalPages"],
                "uploaded_files": upload_result["uploadedFiles"],
                "status": upload_result["status"]
            }
        
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