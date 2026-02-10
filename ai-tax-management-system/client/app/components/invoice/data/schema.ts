import { z } from 'zod'

export const invoiceSchema = z.object({
  invoiceId: z.string(),
  invoiceNumber: z.string(),
  urn: z.string(),
  documentUrl: z.string(),
  projectNumber: z.string(),
  invoiceDetail: z.array(z.object({
    invoiceDetailId: z.string(),
    itemName: z.string(),
    quantity: z.number(),
    unitPrice: z.number(),
    taxPercentage: z.number(),
    discountPercentage: z.number(),
    extendedPrice: z.number(),
  })).optional(),
  subTotalAmount: z.number(),
  vatPercentage: z.number(),
  vatAmount: z.number(),
  discountAmount: z.number(),
  whtPercentage: z.number(),
  whtAmount: z.number(),
  totalAmount: z.number(),
  currency: z.string(),
  createdAt: z.string(),
  updatedAt: z.string(),
})

export type Invoice = z.infer<typeof invoiceSchema>
