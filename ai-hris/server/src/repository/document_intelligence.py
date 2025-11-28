from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
import numpy as np
from src.config.env import AppConfig

class DocumentIntelligenceRepository:
    def __init__(self, config: AppConfig):
        self.document_intelligence_endpoint = config.DOCUMENT_INTELLIGENCE_ENDPOINT
        self.document_intelligence_key = config.DOCUMENT_INTELLIGENCE_KEY
        self.document_intelligence_client  = DocumentIntelligenceClient(
            endpoint=self.document_intelligence_endpoint, credential=AzureKeyCredential(self.document_intelligence_key)
        )

    def _format_bounding_box(self, bounding_box):
        if not bounding_box:
            return "N/A"
        reshaped_bounding_box = np.array(bounding_box).reshape(-1, 2)
        return ", ".join(["[{}, {}]".format(x, y) for x, y in reshaped_bounding_box])

    def analyze_read(self, document_path: str) -> AnalyzeResult:
        with open(document_path, "rb") as f:
            poller = self.document_intelligence_client.begin_analyze_document(
                "prebuilt-read", AnalyzeDocumentRequest(bytes_source=f.read())
            )
        result: AnalyzeResult = poller.result()
        
        return result
    
    def analyze_layout(self, document_path: str) -> AnalyzeResult:
        with open(document_path, "rb") as f:
            poller = self.document_intelligence_client.begin_analyze_document(
                "prebuilt-layout", AnalyzeDocumentRequest(bytes_source=f.read())
            )
        result: AnalyzeResult = poller.result()
        
        return result

