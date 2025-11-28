from semantic_kernel.kernel_pydantic import KernelBaseModel

class ClassificationResult(KernelBaseModel):
    document_type: str
    confidence_score: float