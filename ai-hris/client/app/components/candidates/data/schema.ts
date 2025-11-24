import { z } from 'zod'

export const candidateSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string(),
  phone: z.string(),
  position: z.string(),
  status: z.enum(['applied', 'reviewing', 'shortlisted', 'rejected', 'hired']),
  appliedDate: z.string(),
  experience: z.number(),
  skills: z.array(z.string()),
  resume: z.string().optional(),
  rating: z.number().min(0).max(5).optional(),
  notes: z.string().optional(),
  cv_url: z.string().optional(),
})

export type Candidate = z.infer<typeof candidateSchema>
