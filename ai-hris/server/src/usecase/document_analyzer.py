from src.repository.document_intelligence import DocumentIntelligenceRepository
from loguru import logger
from src.llm.llm_sk import LLMService
from src.domain.document_analyzer import KartuKeluargaResponse, KartuKeluargaBoundingBox, BukuTabungan, LegalDocumentResponse, KartuKeluarga, DocumentResponse, OfferingLetterContent, OfferingLetterData, ExtractedDocumentContent
from src.domain.document_classification import ClassificationResult
import numpy as np
from src.common.const import DocumentType

class DocumentAnalyzer:
    def __init__(self, doc_intel_repo: DocumentIntelligenceRepository, llm_service: LLMService):
        self.doc_intel_repo = doc_intel_repo
        self.llm_service = llm_service
    
    def _extract_bounding_boxes(self, result):
        """Extract bounding boxes from paragraphs in the analysis result."""
        bounding_boxes = []
        
        if result.paragraphs:
            for paragraph in result.paragraphs:
                if hasattr(paragraph, 'bounding_regions') and paragraph.bounding_regions:
                    # Extract bounding regions which contain pageNumber and polygon
                    for region in paragraph.bounding_regions:
                        polygons = []
                        page_number = 1
                        
                        if hasattr(region, 'page_number'):
                            page_number = region.page_number
                        elif hasattr(region, 'pageNumber'):
                            page_number = region.pageNumber
                        
                        if hasattr(region, 'polygon'):
                            polygons = list(region.polygon) if isinstance(region.polygon, (list, tuple)) else []
                        
                        if polygons:
                            bounding_box = KartuKeluargaBoundingBox(
                                content=getattr(paragraph, 'content', ''),
                                page_number=page_number,
                                polygons=polygons
                            )
                            bounding_boxes.append(bounding_box)
        
        return bounding_boxes
    
    async def analyze_document_kk(self, document_path: str) -> KartuKeluargaResponse:
        try:
            result = self.doc_intel_repo.analyze_read(document_path=document_path)
            
            # Extract bounding boxes from paragraphs
            bounding_boxes = self._extract_bounding_boxes(result)
            
            kartu_keluarga_structured = await self.llm_service.kartu_keluarga_extractor(result.content)

            response = KartuKeluargaResponse(
                content=result.content,
                structured_data=kartu_keluarga_structured,
                bounding_boxes=bounding_boxes
            )

            return response
        except Exception as e:
            logger.error(f"Error in analyze_document use case: {e}")
            raise

    async def classify_legal_document(self, document_content: str) -> ClassificationResult:
        try:
            classification_result = await self.llm_service.legal_document_classification(document_text=document_content)
            return classification_result
        except Exception as e:
            logger.error(f"Error in classify_legal_document use case: {e}")
            raise

    async def upload_document(self, document_path: str, candidate_id: str = None) -> LegalDocumentResponse:
        try:
            # flow: extract content -> classify document -> extract structured data based on type
            # extract raw content
            document_content = self.doc_intel_repo.analyze_read(document_path=document_path)

            # classify document type
            document_type = await self.classify_legal_document(document_content=document_content.content)
            doc_type = document_type.get('category', None)
            
            if doc_type and doc_type == DocumentType.KK.value:
                # bounding_boxes = self._extract_bounding_boxes(document_content)
                kartu_keluarga_structured: KartuKeluarga = await self.llm_service.kartu_keluarga_extractor(document_content.content)
                response = LegalDocumentResponse(
                    type=DocumentType.KK.value,
                    name="",
                    last_updated="",
                    url="",
                    structured_data=kartu_keluarga_structured,
                )
                return response
            elif doc_type and doc_type == DocumentType.BukuTabungan.value:
                buku_tabungan_structured: BukuTabungan = await self.llm_service.buku_tabungan_extractor(document_content.content)
                response = LegalDocumentResponse(
                    type=DocumentType.BukuTabungan.value,
                    name="",
                    last_updated="",
                    url="",
                    structured_data=buku_tabungan_structured,
                )
                return response
            elif doc_type and doc_type == DocumentType.KTP.value:
                ktp_structured = await self.llm_service.ktp_extractor(document_content.content)
                response = LegalDocumentResponse(
                    type=DocumentType.KTP.value,
                    name="",
                    last_updated="",
                    url="",
                    structured_data=ktp_structured,
                )
                return response
            else:
                return {
                    'content': document_content.content,
                    'document_type': document_type.model_dump() if hasattr(document_type, 'model_dump') else document_type
                }
        except Exception as e:
            logger.error(f"Error in upload_document use case: {e}")
            raise

    async def analyze_offering_letter(self, document_path: str) -> DocumentResponse:
        try:
            is_signed = False
            content = ""
            result = self.doc_intel_repo.analyze_layout(document_path=document_path)

            content = result.content
            if result.styles and len(result.styles) > 0:
                is_signed = result.styles[0].is_handwritten

            content = await self.llm_service.offering_letter_content_analysis(offering_letter_content=content)

            response = DocumentResponse(
                type=DocumentType.SignedOfferLetter.value,
                name="",
                last_updated="",
                url="",
                extracted_content=ExtractedDocumentContent(
                    bounding_boxes=[],
                    content=result.content,
                    structured_data={
                        "is_signed": is_signed,
                        "position": content.get('position', ''),
                        "start_date": content.get('start_date', ''),
                        "salary": content.get('salary', ''),
                        "benefits": content.get('benefits', []),
                    }
                )
            )

            return response
        except Exception as e:
            logger.error(f"Error in analyze_document_layout use case: {e}")
            raise