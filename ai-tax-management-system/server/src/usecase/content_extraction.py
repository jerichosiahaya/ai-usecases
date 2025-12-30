from typing import Dict, Any, Optional, List
import asyncio
import re
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.storage import MinioStorageRepository
from src.repository.storage import AzureBlobStorageRepository
from src.repository.messaging import RabbitMQRepository
from src.repository.llm.llm_service import LLMService
from src.repository.database import AzureCosmosDBRepository
from loguru import logger
from src.common.const import ContentType
import uuid

class ContentExtraction:
    def __init__(
        self, 
        content_understanding_repo: ContentUnderstandingRepository,
        azure_blob_storage_repo: AzureBlobStorageRepository,
        rabbitmq_repo: Optional[RabbitMQRepository] = None,
        minio_storage_repo: Optional[MinioStorageRepository] = None,
        llm_service_repo: Optional[LLMService] = None,
        azure_cosmos_repo: Optional[AzureCosmosDBRepository] = None
    ):
        
        self.content_understanding_repo = content_understanding_repo
        self.azure_blob_storage_repo = azure_blob_storage_repo
        self.rabbitmq_repo = rabbitmq_repo
        self.minio_storage_repo = minio_storage_repo
        self.llm_service_repo = llm_service_repo
        self.azure_cosmos_repo = azure_cosmos_repo

    def _extract_content(self, file, upload_id: str, original_filename: str) -> Dict[str, Any]:

        try:
            file_info = self.minio_storage_repo.upload_file(
                file=file, case_id=upload_id, original_filename=original_filename
            )

            return None
        
        except Exception as e:
            logger.error(f"Error extracting content from {original_filename}: {e}")
            raise

    def _retrieve_file(self, file_id: str) -> bytes:
        try:
            file_bytes = self.azure_blob_storage_repo.download_file(file_id=file_id)
            return file_bytes
        except Exception as e:
            logger.error(f"Error retrieving file {file_id}: {e}")
            raise

    def _extract_urn_from_content(self, content: str) -> Optional[str]:
        """
        Extract URN (Unique Reference Number) from document content using regex.
        Looks for the first numeric sequence at the beginning of the content (typically 10+ digits).
        
        Args:
            content: The extracted document content text
            
        Returns:
            The extracted URN or None if not found
        """
        try:
            # Match the first sequence of digits (typically 10+ digits at the start)
            # Strip whitespace and newlines first
            content_stripped = content.strip()
            
            # Look for the first sequence of digits
            match = re.search(r'\b\d{10,}\b', content_stripped)
            
            if match:
                urn = match.group(0)
                logger.info(f"Extracted URN from content: {urn}")
                return urn
            
            logger.warning("No URN found in document content")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting URN from content: {e}")
            return None

    async def _wait_for_analysis_result(
        self, 
        request_id: str,
        max_retries: int = 35,
        retry_interval: int = 3
    ) -> Dict[str, Any]:
        """
        Poll the analyzer results endpoint until the analysis is complete
        
        Args:
            request_id: The request ID from the initial analyze_invoice call
            max_retries: Maximum number of retry attempts (default 15 = 15 seconds with 1s interval)
            retry_interval: Seconds to wait between retries (default 1)
            
        Returns:
            Dictionary with the final analysis results when status is not "Running"
            
        Raises:
            TimeoutError: If max_retries exceeded while status is still "Running"
            Exception: If analyzer returns an error status
        """
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get the current analysis result
                result = self.content_understanding_repo.get_analyzer_results(request_id)
                status = result.get("status")
                
                logger.debug(f"Analysis status for request {request_id}: {status}")
                
                # Check if analysis is complete
                if status == "Succeeded":
                    logger.info(f"Analysis completed successfully: {request_id}")

                    # hit llm service for content classification if available
                    if self.llm_service_repo:
                        try:
                            content = result['result']['contents'][0]['markdown']
                            urn = self._extract_urn_from_content(content)
                            content_classification = await self.llm_service_repo.get_content_classification(
                                document_text=content
                            )
                            content_classification_data = content_classification.get("classification", ContentType.Unknown.value)

                            if content_classification_data == ContentType.Invoice.value:
                                # call invoice extraction
                                result = await self.llm_service_repo.get_invoice_extraction(
                                    document_text=content
                                )
                                result['urn'] = urn
                                result['invoiceId'] = str(uuid.uuid4())

                                # save the result to cosmos db
                                if self.azure_cosmos_repo and urn:
                                    self.azure_cosmos_repo.create_document(
                                        document_data=result,
                                        container_id="invoices"
                                    )

                            elif content_classification_data == ContentType.TaxInvoice.value:
                                result = await self.llm_service_repo.get_tax_invoice_extraction(
                                    document_text=content)
                                result['urn'] = urn
                                result['taxInvoiceId'] = str(uuid.uuid4())
                                if self.azure_cosmos_repo and urn:
                                    self.azure_cosmos_repo.create_document(
                                        document_data=result,
                                        container_id="tax-invoices"
                                    )
                            elif content_classification_data == ContentType.GeneralLedger.value:
                                result = await self.llm_service_repo.get_gl_extraction(
                                    document_text=content)
                            else:
                                result = {"message": "Content type is Unknown, no extraction performed."}

                            logger.info(f"Content classification completed for {request_id}")
                        except Exception as e:
                            logger.error(f"Error getting content classification for {request_id}: {e}")
                    else:
                        logger.warning("LLM service repository not available, skipping content classification")

                    return result
                elif status in ["Failed", "AnalyzeError"]:
                    logger.error(f"Analysis failed with status {status}: {request_id}")
                    raise Exception(f"Analysis failed with status: {status}. Result: {result}")
                elif status == "Running":
                    # Still processing, wait and retry
                    retry_count += 1
                    logger.debug(f"Analysis still running, retrying... ({retry_count}/{max_retries})")
                    await asyncio.sleep(retry_interval)
                    continue
                else:
                    logger.warning(f"Unknown analysis status: {status}")
                    retry_count += 1
                    await asyncio.sleep(retry_interval)
                    continue
                    
            except Exception as e:
                logger.error(f"Error checking analysis results for {request_id}: {e}")
                raise
        
        # Max retries exceeded
        raise TimeoutError(f"Analysis did not complete within {max_retries * retry_interval} seconds for request {request_id}")

    async def process_documents_in_folder(self, file_id: str) -> List[Dict[str, Any]]:
        SUPPORTED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}

        try:
            logger.info(f"Processing documents in folder: {file_id}")
            
            # List all files in the folder
            files = self.azure_blob_storage_repo.list_files(file_id)
            logger.info(f"Found {len(files)} files in folder {file_id}")
            
            analysis_results = []
            
            # Loop through each file
            for file_info in files:
                file_url = file_info.get("url")
                blob_name = file_info.get("blob_name")
                
                if not file_url:
                    logger.warning(f"Skipping file without URL: {blob_name}")
                    continue
                
                # Check if file is a document (PDF, image, etc.)
                file_extension = blob_name.rsplit('.', 1)[-1].lower() if '.' in blob_name else ''
                
                if file_extension not in SUPPORTED_EXTENSIONS:
                    logger.debug(f"Skipping unsupported file type: {blob_name}")
                    continue
                
                try:
                    logger.info(f"Analyzing document: {blob_name}")
                    
                    # Step 1: Send to content understanding (invoice analyzer) - returns immediately with request ID
                    initial_response = self.content_understanding_repo.analyze_invoice(file_url)
                    request_id = initial_response.get("id")
                    
                    if not request_id:
                        logger.error(f"No request ID returned from analyzer for {blob_name}")
                        analysis_results.append({
                            "blob_name": blob_name,
                            "file_url": file_url,
                            "error": "No request ID returned from analyzer"
                        })
                        continue
                    
                    logger.info(f"Analysis initiated for {blob_name}, request ID: {request_id}")
                    
                    # Step 2: Wait for analysis to complete by polling the results endpoint
                    logger.debug(f"Waiting for analysis to complete for {blob_name}...")
                    final_result = await self._wait_for_analysis_result(request_id)
                    
                    logger.info(f"Successfully analyzed: {blob_name}")
                    
                    analysis_results.append({
                        "blob_name": blob_name,
                        "file_url": file_url,
                        "request_id": request_id,
                        "analysis_result": final_result
                    })
                    
                except TimeoutError as e:
                    logger.error(f"Timeout waiting for analysis of {blob_name}: {e}")
                    analysis_results.append({
                        "blob_name": blob_name,
                        "file_url": file_url,
                        "error": f"Timeout: {str(e)}"
                    })
                except Exception as e:
                    logger.error(f"Error analyzing document {blob_name}: {e}")
                    analysis_results.append({
                        "blob_name": blob_name,
                        "file_url": file_url,
                        "error": str(e)
                    })
            
            logger.info(f"Completed processing {len(analysis_results)} documents from folder {file_id}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error processing documents in folder {file_id}: {e}")
            raise

    async def process_message(self, message: Dict[str, Any]) -> None:
        try:
            # file_id in status
            document_id = message.get("document_id")
            if not document_id:
                logger.error("Message missing 'document_id'")
                return

            logger.info(f"Processing content extraction for document ID: {document_id}")

            result = await self.process_documents_in_folder(file_id=document_id)

            self.azure_cosmos_repo.update_document(
                document_id=document_id,
                update_data={
                    "urn": next((res.get('analysis_result', {}).get('urn') for res in result if res.get('analysis_result') and res.get('analysis_result', {}).get('urn')), None),
                    "status": "completed"
                },
                container_id="uploads",
                partial_update=True
            )

            logger.info(f"Successfully processed content extraction for document ID: {document_id}")

        except Exception as e:
            logger.error(f"Error processing message {message}: {e}")
            raise