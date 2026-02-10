import { z } from 'zod'

export const taxInvoiceSchema = z.object({
  taxInvoiceId: z.string(),
  urn: z.string(),
  documentUrl: z.string(),
  taxInvoiceNumber: z.string(),
  invoiceNumber: z.string(),
  taxInvoiceDate: z.string(),
  namaPengusahaKenaPajak: z.string(),
  alamatPengusahaKenaPajak: z.string(),
  npwpPengusahaKenaPajak: z.string(),
  namaPembeliKenaPajak: z.string(),
  alamatPembeliKenaPajak: z.string(),
  npwpPembeliKenaPajak: z.string(),
  nikPembeliKenaPajak: z.string(),
  nomorPasporPembeliKenaPajak: z.string(),
  emailPembeliKenaPajak: z.string(),
  taxInvoiceDetail: z.array(z.object({
    taxInvoiceDetailId: z.string(),
    itemCode: z.string(),
    itemName: z.string(),
    price: z.number(),
    quantity: z.number(),
    taxBaseWht: z.number(),
  })).optional(),
  totalTaxBaseWht: z.number(),
  dikurangiPotonganHarga: z.number(),
  dikurangiUangMukaYangTelahDiterima: z.number(),
  dasarPengenaanPajak: z.number(),
  jumlahPpn: z.number(),
  jumlahPpnbm: z.number(),
  createdAt: z.string(),
  updatedAt: z.string(),
})

export type TaxInvoice = z.infer<typeof taxInvoiceSchema>
