from semantic_kernel.kernel_pydantic import KernelBaseModel

class KartuKeluargaBoundingBox(KernelBaseModel):
    content: str
    page_number: int
    polygons: list[int]

class KartuKeluargaResponse(KernelBaseModel):
    content: str
    structured_data: dict
    bounding_boxes: list[KartuKeluargaBoundingBox] = []

class FamilyMemberDetail(KernelBaseModel):
    name: str
    nik: str
    gender: str
    relationship: str
    birth_date: str
    religion: str
    education: str
    occupation: str
    marital_status: str
    blood_type: str

# structure for Kartu Keluarga document
class KartuKeluarga(KernelBaseModel):
    family_head_name: str
    family_number: str
    address: str
    rt_rw: str
    village: str
    district: str
    city: str
    province: str
    postal_code: str
    family_members: list[FamilyMemberDetail]

# structure for Buku Tabungan document
class BukuTabungan(KernelBaseModel):
    account_holder_name: str
    account_number: str
    bank_name: str
    branch_name: str
    account_type: str

# structure for KTP document
class KTP(KernelBaseModel):
    nik: str
    name: str
    birth_place: str
    birth_date: str
    gender: str
    address: str
    rt_rw: str
    village: str
    district: str
    city: str
    province: str
    religion: str
    marital_status: str
    occupation: str
    nationality: str

class LegalDocumentResponse(KernelBaseModel):
    type: str
    name: str
    structured_data: dict
    url: str
    last_updated: str

class OfferingLetterContent(KernelBaseModel):
    position: str
    start_date: str
    salary: str
    benefits: list[str]

class OfferingLetterData(KernelBaseModel):
    is_signed: bool
    content: OfferingLetterContent

class ExtractedDocumentContent(KernelBaseModel):
    bounding_boxes: list[dict]
    content: str
    structured_data: dict

class DocumentResponse(KernelBaseModel):
    type: str
    name: str
    last_updated: str
    url: str
    extracted_content: ExtractedDocumentContent

    