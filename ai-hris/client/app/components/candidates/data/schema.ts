import { z } from 'zod'

const extractedContentSchema = z.object({
  text: z.string(),
  tables: z.array(z.any()).optional(),
  bounding_boxes: z.array(z.any()).optional(),
})

const documentSchema = z.object({
  type: z.string(),
  name: z.string(),
  url: z.string(),
  last_updated: z.string(),
  extracted_content: extractedContentSchema.optional(),
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

export const candidateSchema = z.object({
  id: z.string(),
  candidate_id: z.string(),
  name: z.string(),
  email: z.string().optional(),
  phone: z.string().optional(),
  position: z.string().optional(),
  status: z.enum(['applied', 'reviewing', 'shortlisted', 'rejected', 'hired']).optional(),
  applied_date: z.string().optional(),
  experience: z.number().optional(),
  skills: z.array(z.string()).optional(),
  rating: z.number().min(0).max(5).optional(),
  notes: z.array(noteSchema).optional(),
  resume: z.array(documentSchema).optional(),
  legal_documents: z.array(documentSchema).optional(),
  cv_url: z.string().optional(),
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
  documents: z.array(documentSchema).optional(),
})

export type Candidate = z.infer<typeof candidateSchema>
