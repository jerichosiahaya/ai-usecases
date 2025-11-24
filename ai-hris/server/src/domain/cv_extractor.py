from semantic_kernel.kernel_pydantic import KernelBaseModel

class EducationHistoryItem(KernelBaseModel):
    institution_name: str
    level_degree: str
    area_of_study: str
    start_date_education: str
    completion_date_education: str

class WorkHistoryItem(KernelBaseModel):
    company_name: str
    previous_job_position: str
    previous_job_industry: str
    year_of_experience: str
    start_date_work: str
    end_date_work: str
    work_model: str
    employment_type: str

class CVAttributeExtractionResponse(KernelBaseModel):
    first_name: str
    middle_name: str
    last_name: str
    gender: str
    email: str
    country: str
    city: str
    address: str
    birth_date: str
    current_employer: str
    linkedin_url: str
    phone_number: str
    postal_code: str
    skills: str
    highest_degree: str
    total_year_of_experience: str
    education_history: list[EducationHistoryItem] = []
    work_history: list[WorkHistoryItem] = []