from typing import Dict, Any, Optional, List
import asyncio
import re
from datetime import datetime
from src.repository.content_understanding import ContentUnderstandingRepository
from src.repository.storage import MinioStorageRepository
from src.repository.storage import AzureBlobStorageRepository
from src.repository.messaging import RabbitMQRepository
from src.repository.llm.llm_service import LLMService
from src.repository.database import AzureCosmosDBRepository
from loguru import logger
from src.common.const import ContentType
import uuid
from pypdf import PdfReader, PdfWriter
from io import BytesIO

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
        file_url: Optional[str] = None,
        blob_name: Optional[str] = None,
        file_id: Optional[str] = None,
        max_retries: int = 35,
        retry_interval: int = 3,
        accumulated_content: Optional[List[str]] = None,
        accumulated_file_urls: Optional[List[str]] = None
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
                            is_document_complete = content_classification.get("is_document_complete", True)

                            if content_classification_data == ContentType.Invoice.value:
                                # call invoice extraction
                                result = await self.llm_service_repo.get_invoice_extraction(document_text=content)
                                result['urn'] = urn
                                result['invoiceId'] = str(uuid.uuid4())
                                result['documentUrl'] = file_url

                                # save the result to cosmos db
                                if self.azure_cosmos_repo and urn:
                                    self.azure_cosmos_repo.create_document(
                                        document_data=result,
                                        container_id="invoices"
                                    )

                            elif content_classification_data == ContentType.TaxInvoice.value:
                                # Initialize accumulated_content if not provided
                                if accumulated_content is None:
                                    accumulated_content = []
                                if accumulated_file_urls is None:
                                    accumulated_file_urls = []
                                
                                # Add current page content and file URL to accumulated lists
                                accumulated_content.append(content)
                                accumulated_file_urls.append(file_url)
                                logger.info(f"Tax invoice page accumulated. Total pages: {len(accumulated_content)}, Complete: {is_document_complete}")
                                
                                if not is_document_complete:
                                    # Document incomplete, return None to skip this page
                                    logger.info(f"Tax invoice incomplete. Accumulated {len(accumulated_content)} pages so far. Continuing to next page.")
                                    return None
                                
                                # Document is complete - merge all accumulated content and PDFs
                                merged_content = "\n\n--- PAGE BREAK ---\n\n".join(accumulated_content)
                                logger.info(f"Tax invoice complete. Extracting from {len(accumulated_content)} merged pages")
                                
                                # Merge PDFs if multiple pages
                                merged_pdf_url = file_url  # Default to last page URL
                                if len(accumulated_file_urls) > 1:
                                    try:
                                        merged_pdf_url = await self._merge_pdfs_from_urls(
                                            file_urls=accumulated_file_urls,
                                            file_id=file_id,
                                            urn=urn
                                        )
                                        logger.info(f"Merged {len(accumulated_file_urls)} PDFs into: {merged_pdf_url}")
                                    except Exception as e:
                                        logger.error(f"Failed to merge PDFs: {e}. Using last page URL.")
                                
                                result = await self.llm_service_repo.get_tax_invoice_extraction(document_text=merged_content)
                                result['urn'] = urn
                                result['taxInvoiceId'] = str(uuid.uuid4())
                                result['documentUrl'] = merged_pdf_url
                                result['total_pages'] = len(accumulated_content)

                                if self.azure_cosmos_repo and urn:
                                    self.azure_cosmos_repo.create_document(
                                        document_data=result,
                                        container_id="tax-invoices"
                                    )
                                
                                # Clear accumulated content and URLs after successful extraction
                                accumulated_content.clear()
                                accumulated_file_urls.clear()
                            elif content_classification_data == ContentType.GeneralLedger.value:
                                result = await self.llm_service_repo.get_gl_extraction(document_text=content)
                                result['documentUrl'] = file_url
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

    async def _merge_pdfs_from_urls(self, file_urls: List[str], file_id: str, urn: Optional[str]) -> str:
        """
        Download multiple PDF files from blob storage URLs, merge them, and upload the merged PDF.
        
        Args:
            file_urls: List of blob storage URLs to merge
            file_id: The folder ID for organizing the merged file
            urn: URN for naming the merged file
            
        Returns:
            URL of the uploaded merged PDF
        """
        try:
            pdf_writer = PdfWriter()
            
            # Download and merge each PDF
            for idx, url in enumerate(file_urls):
                logger.info(f"Downloading PDF {idx + 1}/{len(file_urls)}: {url}")
                
                # Extract blob name from URL to download from blob storage
                # URL format: https://<account>.blob.core.windows.net/<container>/<folder>/<blob_name>
                blob_path = '/'.join(url.split('/')[-2:])  # Get folder/blob_name part
                
                # Download the PDF bytes
                pdf_bytes = self.azure_blob_storage_repo.download_blob(blob_name=blob_path)
                
                # Read the PDF and add pages to writer
                pdf_reader = PdfReader(BytesIO(pdf_bytes))
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                logger.debug(f"Added {len(pdf_reader.pages)} pages from {blob_path}")
            
            # Write merged PDF to bytes
            merged_pdf_buffer = BytesIO()
            pdf_writer.write(merged_pdf_buffer)
            merged_pdf_buffer.seek(0)
            
            # Generate filename for merged PDF
            merged_filename = f"merged_tax_invoice_{urn or uuid.uuid4()}.pdf"
            
            # Upload merged PDF to blob storage
            logger.info(f"Uploading merged PDF: {merged_filename}")
            upload_result = self.azure_blob_storage_repo.upload_file(
                file=merged_pdf_buffer,
                file_id=file_id,
                original_filename=merged_filename,
                activity_id=str(uuid.uuid4()),
                content_type="application/pdf"  # This will trigger inline content-disposition
            )
            
            merged_url = upload_result.get("url")
            logger.info(f"Merged PDF uploaded successfully: {merged_url}")
            
            return merged_url
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            raise

    async def process_documents_in_folder(self, file_id: str) -> List[Dict[str, Any]]:
        SUPPORTED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'tiff', 'bmp'}

        try:
            logger.info(f"Processing documents in folder: {file_id}")
            
            # List all files in the folder
            files = self.azure_blob_storage_repo.list_files(file_id)
            logger.info(f"Found {len(files)} files in folder {file_id}")
            
            # Sort files numerically by blob_name to ensure consistent processing order (pdf_1, pdf_2, ..., pdf_10, etc.)
            def natural_sort_key(f):
                blob_name = f.get("blob_name", "")
                # Extract numeric part from filename for natural sorting
                # e.g., "pdf_1" -> extract 1, "pdf_10" -> extract 10
                import re
                parts = []
                for part in re.split(r'(\d+)', blob_name):
                    if part.isdigit():
                        parts.append((0, int(part)))  # Numeric parts sort as numbers
                    else:
                        parts.append((1, part))  # String parts sort lexicographically
                return parts
            
            files = sorted(files, key=natural_sort_key)
            logger.info(f"Files sorted numerically: {[f.get('blob_name') for f in files]}")
            
            analysis_results = []
            accumulated_tax_invoice_content = []  # Track incomplete tax invoice pages
            accumulated_tax_invoice_urls = []  # Track file URLs for incomplete tax invoice pages
            
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
                    final_result = await self._wait_for_analysis_result(
                        request_id,
                        file_url=file_url,
                        blob_name=blob_name,
                        file_id=file_id,
                        accumulated_content=accumulated_tax_invoice_content,
                        accumulated_file_urls=accumulated_tax_invoice_urls
                    )
                    
                    # Check if result is None (incomplete tax invoice page)
                    if final_result is None:
                        logger.info(f"Incomplete page for {blob_name}, continuing to next page")
                        continue
                    
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
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat()
                },
                container_id="uploads",
                partial_update=True
            )

            logger.info(f"Successfully processed content extraction for document ID: {document_id}")

        except Exception as e:
            logger.error(f"Error processing message {message}: {e}")
            raise