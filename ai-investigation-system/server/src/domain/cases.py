from semantic_kernel.kernel_pydantic import KernelBaseModel

class IntentResponse(KernelBaseModel):
    intent: str

class SourceReferenceDetail(KernelBaseModel):
    document_id: str
    content_snippet: str
    file_name: str
    file_url: str

class CaseChatResponse(KernelBaseModel):
    response: str
    source_references: list[SourceReferenceDetail]

class CaseDataAnalystResponse(KernelBaseModel):
    findings: str
    risks: str
    connections: str