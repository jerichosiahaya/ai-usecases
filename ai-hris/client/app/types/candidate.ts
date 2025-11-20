export interface Candidate {
  id: string
  name: string
  email: string
  phone: string
  role: string
  status: 'New' | 'Screening' | 'Interview' | 'Offer' | 'Hired' | 'Rejected'
  appliedDate: string
  score?: number
  summary?: string
  skills?: string[]
  experience?: number // years
  // New fields for detailed view
  avatar?: string
  origin?: string
  overallScore?: number
  location?: string
  workType?: string
  workModel?: string
  currentEmployer?: string
  currentSalary?: string
  expectedSalary?: string
  gender?: string
  birthdate?: string
  address?: string
  education?: {
    university: string
    qualification: string
    graduationYear: string
  }
}
