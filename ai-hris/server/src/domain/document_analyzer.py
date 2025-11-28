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