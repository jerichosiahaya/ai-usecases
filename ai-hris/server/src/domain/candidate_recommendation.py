from pydantic import BaseModel

class CandidateData(BaseModel):
    candidate_id: str
    candidate_name: str
    candidate_skills: str
    candidate_education_history: str
    candidate_work_history: str

class JobData(BaseModel):
    job_title: str
    job_description: str
    job_skills: str
    job_education_requirements: str
