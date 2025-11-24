from semantic_kernel.kernel_pydantic import KernelBaseModel

class CVScoringAttributeDetails(KernelBaseModel):
    subattribute_name: str
    percentage: int

class CVScoringAttribute(KernelBaseModel):
    attribute_name: str
    attribute_details: list[CVScoringAttributeDetails]

class CVScoringResponse(KernelBaseModel):
    data: list[CVScoringAttribute]