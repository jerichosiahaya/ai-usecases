import { z } from 'zod'

export const jobSchema = z.object({
  id: z.string(),
  title: z.string(),
  department: z.string(),
  location: z.string(),
  type: z.enum(['Full-time', 'Part-time', 'Contract', 'Internship']),
  status: z.enum(['Open', 'Closed', 'Draft']),
  postedDate: z.string(),
  applicants: z.number(),
  description: z.string().optional(),
  requirements: z.array(z.string()).optional(),
  salary: z.object({
    min: z.number(),
    max: z.number(),
    currency: z.string()
  }).optional(),
  skills: z.array(z.string()).optional(),
  benefits: z.array(z.string()).optional(),
  hiringTeam: z.object({
    hiringManager: z.object({
      name: z.string(),
      avatar: z.string().optional()
    }),
    recruiter: z.object({
      name: z.string(),
      avatar: z.string().optional()
    })
  }).optional(),
})

export type Job = z.infer<typeof jobSchema>
