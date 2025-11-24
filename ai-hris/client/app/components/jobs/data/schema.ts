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
})

export type Job = z.infer<typeof jobSchema>
