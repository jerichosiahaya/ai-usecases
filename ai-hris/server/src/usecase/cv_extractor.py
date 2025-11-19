import PyPDF2
import io
from src.llm.llm_sk import LLMService
import base64
import docx # not used in the final code, but kept for reference
import docx2txt
from loguru import logger

class CVExtractor:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def extract_text_from_pdf(self, pdf_file_path: str = None, pdf_bytes: bytes = None) -> str:
        try:
            if pdf_bytes:
                pdf_file = io.BytesIO(pdf_bytes)
            elif pdf_file_path:
                pdf_file = open(pdf_file_path, 'rb')
            else:
                raise ValueError("Either pdf_file_path or pdf_bytes must be provided")
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if pdf_file_path:
                pdf_file.close()
                
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_docx(self, docx_file_path: str = None, docx_bytes: bytes = None) -> str:
        try:
            if docx_bytes:
                # Use docx2txt for bytes input
                docx_file = io.BytesIO(docx_bytes)
                text = docx2txt.process(docx_file)
            elif docx_file_path:
                # Use docx2txt for file path input
                text = docx2txt.process(docx_file_path)
            else:
                raise ValueError("Either docx_file_path or docx_bytes must be provided")
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")

    def extract_text_from_doc(self, doc_file_path: str = None, doc_bytes: bytes = None) -> str:
        try:
            raise NotImplementedError("DOC file extraction is not implemented. Please convert to DOCX format or use a different approach.") 
        except Exception as e:
            raise Exception(f"Error extracting text from DOC: {str(e)}")
        
    def _decode_base64_file(self, base64_file: str) -> bytes:
        try:
            # Decode the base64 string
            decoded_bytes = base64.b64decode(base64_file)
            return decoded_bytes
        except Exception as e:
            raise ValueError(f"Invalid base64 file: {str(e)}")
    
    def _is_pdf(self, file_bytes: bytes) -> bool:
        """Simple check if the file bytes represent a PDF by checking the header"""
        return file_bytes.startswith(b'%PDF-')

    def _is_docx(self, file_bytes: bytes) -> bool:
        """Simple check if the file bytes represent a DOCX by checking the header"""
        # DOCX files are ZIP archives that start with PK
        return file_bytes.startswith(b'PK')

    def _is_doc(self, file_bytes: bytes) -> bool:
        """Simple check if the file bytes represent a DOC by checking the header"""
        # Legacy DOC files have specific signatures
        return (file_bytes.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1') or  # OLE2 signature
                file_bytes.startswith(b'\xdb\xa5\x2d\x00') or  # Alternative DOC signature
                file_bytes.startswith(b'\xec\xa5\xc1\x00'))   # Another DOC signature

    def _detect_file_type(self, file_bytes: bytes) -> str:
        """Detect the file type based on file headers"""
        if self._is_pdf(file_bytes):
            return 'pdf'
        elif self._is_docx(file_bytes):
            return 'docx'
        elif self._is_doc(file_bytes):
            return 'doc'
        else:
            return 'unknown'

    async def extract(self, pdf_file_path: str = None, pdf_bytes: bytes = None, base64_cv: str = None) -> dict:
        try:
            logger.info("Starting CV extraction process")
            if pdf_bytes or pdf_file_path:
                file_extension = pdf_file_path.lower().split('.')[-1]
                if file_extension == 'pdf':
                    cv_text = self.extract_text_from_pdf(pdf_file_path, pdf_bytes)
                elif file_extension == 'docx':
                    cv_text = self.extract_text_from_docx(docx_file_path=pdf_file_path, docx_bytes=pdf_bytes)
                elif file_extension == 'doc':
                    cv_text = self.extract_text_from_doc(doc_file_path=pdf_file_path, doc_bytes=pdf_bytes)
                else:
                    raise ValueError("The provided file is not a valid PDF, DOCX, or DOC file.")
            elif base64_cv:
                cv_file = self._decode_base64_file(base64_cv)
                file_type = self._detect_file_type(cv_file)
                if file_type == 'pdf':
                    cv_text = self.extract_text_from_pdf(pdf_bytes=cv_file)
                elif file_type == 'docx':
                    cv_text = self.extract_text_from_docx(docx_bytes=cv_file)
                elif file_type == 'doc':
                    cv_text = self.extract_text_from_doc(doc_bytes=cv_file)
                else:
                    raise ValueError("The provided base64 string does not represent a valid PDF, DOCX, or DOC file.")
            else:
                raise ValueError("No valid file input provided")

            result = await self.llm_service.extract_cv_attributes(cv_text=cv_text)

            return result
            
        except Exception as e:
            raise Exception(f"Error extracting CV attributes: {str(e)}")
