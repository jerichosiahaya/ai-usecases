import { z } from 'zod'

const boundingBoxSchema = z.object({
  content: z.string(),
  page_number: z.number(),
  polygons: z.array(z.number()),
})

const familyMemberDetailSchema = z.object({
  name: z.string(),
  nik: z.string(),
  gender: z.string(),
  birth_date: z.string(),
  religion: z.string(),
  education: z.string(),
  occupation: z.string(),
  marital_status: z.string(),
  blood_type: z.string().optional().nullable(),
})

const kartuKeluargaStructuredSchema = z.object({
  family_head_name: z.string(),
  family_number: z.string(),
  address: z.string(),
  rt_rw: z.string(),
  village: z.string(),
  district: z.string(),
  city: z.string(),
  province: z.string(),
  postal_code: z.string(),
  family_members: z.array(familyMemberDetailSchema),
})

const ktpStructuredSchema = z.object({
  nik: z.string().optional(),
  name: z.string().optional(),
  birth_place: z.string().optional(),
  birth_date: z.string().optional(),
  gender: z.string().optional(),
  religion: z.string().optional(),
  marital_status: z.string().optional(),
  occupation: z.string().optional(),
  nationality: z.string().optional(),
  address: z.string().optional(),
  rt_rw: z.string().optional(),
  village: z.string().optional(),
  district: z.string().optional(),
  city: z.string().optional(),
  province: z.string().optional(),
}).passthrough()

const extractedContentSchema = z.object({
  boundingBoxes: z.array(boundingBoxSchema).optional(),
  content: z.string().optional(),
  structured_data: z.any().optional(),
}).passthrough()

// deprecated, use legalDocumentSchemaV2 instead
const legalDocumentSchema = z.object({
  type: z.string(),
  name: z.string(),
  url: z.string(),
  lastUpdated: z.string(),
  extractedContent: extractedContentSchema.optional(),
})

const legalDocumentSchemaV2 = z.object({
  type: z.string(),
  name: z.string(),
  last_updated: z.string(),
  url: z.string(),
  extracted_content: extractedContentSchema.optional(),
})

const resumeDocumentSchema = z.object({
  type: z.string().default('RESUME'),
  name: z.string(),
  url: z.string(),
  lastUpdated: z.string(),
  extractedContent: z.object({
    content: z.string(),
    tables: z.array(z.any()).optional(),
    boundingBoxes: z.array(z.any()).optional(),
  }).optional(),
})

const offeringLetterSchema = z.object({
  type: z.string().default('Signed Offering Letter'),
  name: z.string(),
  url: z.string(),
  last_updated: z.string(),
  extracted_content: extractedContentSchema.optional(),
})

const bukuTabunganStructuredSchema = z.object({
  account_holder_name: z.string().optional(),
  account_number: z.string().optional(),
  account_type: z.string().optional(),
  bank_name: z.string().optional(),
  branch_name: z.string().optional(),
})

const bukuTabunganSchema = z.object({
  type: z.string().default('Buku Tabungan'),
  name: z.string(),
  url: z.string(),
  lastUpdated: z.string(),
  extractedContent: extractedContentSchema.optional(),
})

const noteSchema = z.object({
  author: z.string(),
  role: z.string(),
  message: z.string(),
})

const addressSchema = z.object({
  detail: z.string(),
  city: z.string(),
  country: z.string(),
  zip: z.number().optional(),
})

const interviewScoreSchema = z.object({
  label: z.string(),
  value: z.number(),
})

const interviewSchema = z.object({
  summary: z.string().optional(),
  score_details: z.array(interviewScoreSchema).optional(),
  interview_scores: z.array(interviewScoreSchema).optional(),
  signals: z.array(z.string()).optional(),
})

const briefDataSchema = z.object({
  occupation: z.string().optional(),
  contact: z.string().optional(),
})

const familyMemberSchema = z.object({
  name: z.string(),
  relationship: z.string(),
  date_of_birth: z.string().optional(),
  brief_data: briefDataSchema.optional(),
})

const salaryFactorSchema = z.object({
  name: z.string(),
  value: z.string(),
})

const marketRangeSchema = z.object({
  min: z.number(),
  max: z.number(),
  currency: z.string(),
})

const salarySchema = z.object({
  expectation: z.number(),
  market_range: marketRangeSchema.optional(),
  status: z.string(),
  confidence: z.number(),
  analysis: z.string(),
  factors: z.array(salaryFactorSchema),
})

const discrepancySchema = z.object({
  category: z.string().optional(),
  field: z.string(),
  severity: z.enum(['low', 'medium', 'high']),
  note: z.string().optional(),
  source: z.object({
    type: z.string(),
    name: z.string(),
    value: z.string().optional(),
  }).optional(),
  target: z.object({
    type: z.string(),
    name: z.string(),
    value: z.string().optional(),
  }).optional(),
})

export const candidateSchema = z.object({
  id: z.string(),
  candidate_id: z.string(),
  name: z.string(),
  photo_url: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  position: z.string().optional(),
  status: z.enum(['applied', 'reviewing', 'shortlisted', 'rejected', 'hired']).optional(),
  applied_date: z.string().optional(),
  experience: z.number().optional(),
  skills: z.array(z.string()).optional(),
  rating: z.number().min(0).max(5).optional(),
  notes: z.array(noteSchema).optional(),
  gender: z.string().optional(),
  date_of_birth: z.string().optional(),
  address: addressSchema.optional(),
  education: z.array(z.object({
    institution: z.string(),
    degree: z.string(),
    field_of_study: z.string(),
    graduation_year: z.number(),
    gpa: z.number(),
  })).optional(),
  work_experiences: z.array(z.object({
    company: z.string(),
    position: z.string(),
    start_date: z.string(),
    end_date: z.string().nullable().optional(),
    is_current: z.boolean().optional(),
    description: z.string().optional(),
  })).optional(),
  family_members: z.array(familyMemberSchema).optional(),
  legal_documents: z.array(legalDocumentSchema).optional(),
  legalDocuments: z.array(legalDocumentSchema).optional(),
  resume: resumeDocumentSchema.optional(),
  offering_letter: offeringLetterSchema.optional(),
  interview: interviewSchema.optional(),
  salary: salarySchema.optional(),
  discrepancies: z.array(discrepancySchema).optional(),
})

export const employeeSchema = z.object({
  id: z.string(),
  employee_id: z.string(),
  name: z.string(),
  photo_url: z.string().optional(),
  email: z.string().optional(),
  phone: z.string().optional(),
  position: z.string().optional(),
  status: z.enum(['active', 'inactive']).optional(),
  joined_date: z.string().optional(),
  experience: z.number().optional(),
  skills: z.array(z.string()).optional(),
  rating: z.number().min(0).max(5).optional(),
  notes: z.array(noteSchema).optional(),
  gender: z.string().optional(),
  date_of_birth: z.string().optional(),
  address: addressSchema.optional(),
  education: z.array(z.object({
    institution: z.string(),
    degree: z.string(),
    field_of_study: z.string(),
    graduation_year: z.number(),
    gpa: z.number(),
  })).optional(),
  work_experiences: z.array(z.object({
    company: z.string(),
    position: z.string(),
    start_date: z.string(),
    end_date: z.string().nullable().optional(),
    is_current: z.boolean().optional(),
    description: z.string().optional(),
  })).optional(),
  family_members: z.array(familyMemberSchema).optional(),
  legal_documents: z.array(legalDocumentSchema).optional(),
  legalDocuments: z.array(legalDocumentSchema).optional(),
  resume: resumeDocumentSchema.optional(),
  offering_letter: offeringLetterSchema.optional(),
  // interview: interviewSchema.optional(),
  salary: salarySchema.optional(),
  discrepancies: z.array(discrepancySchema).optional(),
})

export type Candidate = z.infer<typeof candidateSchema>
export type Employee = z.infer<typeof employeeSchema>
export type KartuKeluargaStructured = z.infer<typeof kartuKeluargaStructuredSchema>
export type KtpStructured = z.infer<typeof ktpStructuredSchema>
export type FamilyMemberDetail = z.infer<typeof familyMemberDetailSchema>
export type BoundingBox = z.infer<typeof boundingBoxSchema>
export type LegalDocument = z.infer<typeof legalDocumentSchema>
export type LegalDocumentSchemaV2 = z.infer<typeof legalDocumentSchemaV2>
export type ResumeDocument = z.infer<typeof resumeDocumentSchema>
export type OfferingLetter = z.infer<typeof offeringLetterSchema>
export type BukuTabungan = z.infer<typeof bukuTabunganSchema>
export type BukuTabunganStructured = z.infer<typeof bukuTabunganStructuredSchema>
export type ExtractedContent = z.infer<typeof extractedContentSchema>
export type Interview = z.infer<typeof interviewSchema>
export type InterviewScore = z.infer<typeof interviewScoreSchema>
export type AiInterviewScore = z.infer<typeof interviewScoreSchema>
export type FamilyMember = z.infer<typeof familyMemberSchema>
export type Salary = z.infer<typeof salarySchema>
export type MarketRange = z.infer<typeof marketRangeSchema>
export type SalaryFactor = z.infer<typeof salaryFactorSchema>
export type Discrepancy = z.infer<typeof discrepancySchema>
