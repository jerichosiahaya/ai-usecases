from typing import Dict, Any
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.blob_storage import BlobStorageRepository
from loguru import logger

class ContentExtraction:
    def __init__(
        self, 
        content_understanding_repo: ContentUnderstandingRepository,
        blob_storage_repo: BlobStorageRepository
    ):
        """
        Initialize the content extraction usecase
        
        Args:
            content_understanding_repo: Repository for Azure AI Content Understanding API
            blob_storage_repo: Repository for Azure Blob Storage
        """
        self.content_understanding_repo = content_understanding_repo
        self.blob_storage_repo = blob_storage_repo

    def extract_content(self, file, upload_id: str, original_filename: str) -> Dict[str, Any]:
        """
        Extract content from a document by uploading to blob storage and analyzing with Content Understanding API
        
        Args:
            file: File object to extract content from
            upload_id: ID of the case to associate with the file
            original_filename: Original name of the file
            
        Returns:
            Dictionary containing the analysis results
            
        Raises:
            Exception: If upload or analysis fails
        """
        try:
            # Step 1: Upload file to blob storage
            logger.info(f"Uploading file {original_filename} to blob storage for case {upload_id}")
            file_info = self.blob_storage_repo.upload_file(file, upload_id, original_filename)
            blob_url = file_info["url"]
            logger.info(f"File uploaded successfully. Blob URL: {blob_url}")
            
            # Step 2: Analyze invoice using Content Understanding API
            logger.info(f"Starting content analysis for {original_filename}")
            analysis_result = self.content_understanding_repo.analyze_invoice(blob_url)
            logger.info(f"Content analysis completed successfully")
            
            # Step 3: Return combined result
            extracted_content = {
                "file_info": file_info,
                "analysis_result": analysis_result,
                "upload_id": upload_id
            }
            
            return extracted_content
        
        except Exception as e:
            logger.error(f"Error extracting content from {original_filename}: {e}")
            raise