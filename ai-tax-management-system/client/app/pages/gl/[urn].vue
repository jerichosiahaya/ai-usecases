<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { GL } from '@/components/gl/data/schema'
import type { Invoice } from '@/components/invoice/data/schema'
import type { TaxInvoice } from '@/components/taxinvoice/data/schema'
import DataTableGLItems from '@/components/gl/components/DataTableGLItems.vue'
import DataTableInvoices from '@/components/invoice/components/DataTableInvoices.vue'
import DataTableTaxInvoices from '@/components/taxinvoice/components/DataTableTaxInvoices.vue'
import { glReconColumns } from '@/components/gl/components/glReconItems'
import { invoiceDetailColumns } from '@/components/invoice/components/columns'
import { taxInvoiceDetailColumns } from '@/components/taxinvoice/components/columns'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  ArrowLeft,
  MapPin,
  Clock,
  Calendar,
  Briefcase,
  Users,
  Building2,
  DollarSign,
  MoreHorizontal,
  Edit,
  Trash2,
  CheckCircle2,
  Save
} from 'lucide-vue-next'
import { Skeleton } from '@/components/ui/skeleton'
import { useGLTransactionDetail, useInvoices, useTaxInvoices } from '@/composables/useTaxApi'
import { formatNumber } from '@/components/gl/components/numbering'

const route = useRoute()
const router = useRouter()
const glId = route.params.urn as string

const { glTransaction, loading: glLoading, error: glError, fetchGLTransactionByUrn } = useGLTransactionDetail()
const { invoices, loading: invoiceLoading, error: invoiceError, fetchInvoices } = useInvoices()
const { taxInvoices, loading: taxInvoiceLoading, error: taxInvoiceError, fetchTaxInvoices } = useTaxInvoices()

// Fetch GL transaction and Invoice on mount
onMounted(async () => {
  await fetchGLTransactionByUrn(glId)
  await fetchInvoices(glId)
  await fetchTaxInvoices(glId)
})

const gl = computed(() => glTransaction.value)
const invoice = computed(() =>
  invoices.value.find(i => i.urn === glId) ?? null
)
const taxInvoice = computed(() =>
  taxInvoices.value.find(t => t.urn === glId) ?? null
)
const showGlDetails = ref(false)
const reconItems = computed(() => gl.value?.glReconItem ?? [])

// const invoicePdfUrl = computed(() =>
//   invoice.value
//     ? `${config.public.apiBase}/api/v1/tax/invoices/${invoice.value.urn}/pdf`
//     : ''
// )

const goBack = () => {
  router.back()
}

const formatCurrency = (amount: number, currency: string) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0
  }).format(amount)
}

const activeTab = ref<'invoice' | 'tax'>('invoice')
</script>

<template>
  <div v-if="glLoading" class="min-h-screen bg-muted/40">
    <div class="max-w-7xl mx-auto p-6 space-y-6">
      
      <!-- Header Skeleton -->
      <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div class="flex items-start gap-4">
          <Skeleton class="h-10 w-10 rounded-md" /> <!-- Back button -->
          <div>
            <Skeleton class="h-8 w-64 mb-1" /> <!-- Title -->
          </div>
        </div>
        
        <div class="flex gap-2">
          <Skeleton class="h-10 w-20" />
          <Skeleton class="h-10 w-20" />
          <Skeleton class="h-10 w-20" />
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- GL Detail Skeleton -->
        <div class="lg:col-span-2 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

            <!-- LEFT COLUMN -->
            <div class="space-y-3">
               <div v-for="i in 8" :key="`left-${i}`" class="flex justify-between items-center min-h-[36px]">
                  <Skeleton class="h-4 w-24" />
                  <Skeleton class="h-4 w-32" />
               </div>
            </div>
            
             <!-- RIGHT COLUMN -->
            <div class="space-y-3">
               <div v-for="i in 8" :key="`right-${i}`" class="flex justify-between items-center min-h-[36px]">
                  <Skeleton class="h-4 w-24" />
                  <Skeleton class="h-4 w-32" />
               </div>
            </div>
          </div>
        </div>
        
        <!-- Table Area Skeleton -->
        <div class="lg:col-span-2 mt-8">
            <Skeleton class="h-10 w-64 mb-4" /> <!-- Tabs -->
            <Skeleton class="h-64 w-full rounded-md" /> <!-- Table -->
        </div>

      </div>
    </div>
  </div>
  
  <div v-else-if="glError" class="flex items-center justify-center min-h-screen">
    <div class="text-center max-w-md">
      <p class="text-destructive font-medium mb-2">Error loading GL transaction</p>
      <p class="text-sm text-muted-foreground mb-4">{{ glError }}</p>
      <Button @click="goBack">Go Back</Button>
    </div>
  </div>
  
  <div v-else-if="gl" class="min-h-screen bg-muted/40">
    <div class="max-w-7xl mx-auto p-6 space-y-6">
      
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div class="flex items-start gap-4">
          <Button variant="ghost" size="icon" @click="goBack" class="mt-1">
            <ArrowLeft class="h-5 w-5" />
          </Button>
          <div>
            <div class="flex items-center gap-3 mb-1">
              <h1 class="text-2xl font-bold tracking-tight text-foreground">URN: {{ gl.urn }}</h1>
            </div>
          </div>
        </div>
        
        <div class="flex gap-2">
          <Button variant="outline">
            Cancel
          </Button>
          <Button variant="outline">
            Save
          </Button>
          <Button variant="outline">
            Export
          </Button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- GL Detail -->
        <div class="lg:col-span-2 space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

            <!-- LEFT COLUMN -->
            <div class="space-y-3">
              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Vendor Name</strong></span>
                <span class="font-medium">{{ gl.vendorName }}</span>
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Reference</strong></span>
                <span class="font-medium">{{ gl.referenceNumber }}</span>
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Document No</strong></span>
                <span class="font-medium">{{ gl.documentNumber }}</span>
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>PO Number</strong></span>
                <span class="font-medium">{{ gl.poNumber }}</span>
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Document Date</strong></span>
                <span class="font-medium">{{ gl.documentDate }}</span>
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>WHT Review</strong></span>
                <span class="font-medium">Transaction</span>
              </div>
            </div>

            <!-- RIGHT COLUMN -->
            <div class="space-y-3">
              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Diff Normal</strong></span>
                <!-- <span class="font-medium">{{ gl.diffNormal }}</span> -->
                 <input
                  type="text"
                  class="w-48 rounded-md border px-2 py-1 text-sm"
                  :value="formatNumber(gl.diffNormal)"
                  :class="gl.diffNormal === 0 ? 'bg-green-100 border-green-500' : 'bg-red-100 border-red-500'"
                  disabled
                />
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Ref</strong></span>
                <!-- <span class="font-medium">{{ gl.ref }}</span> -->
                 <input
                  type="text"
                  class="w-48 rounded-md border px-2 py-1 text-sm"
                  placeholder="Input Text"
                />
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>1st Vouching</strong></span>
                <!-- <span class="font-medium">{{ gl.firstVouching }}</span> -->
                 <input
                  type="text"
                  class="w-48 rounded-md border px-2 py-1 text-sm"
                  v-model="gl.firstVouching"
                  placeholder="Input Text"
                />
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>2nd Reviewer</strong></span>
                <!-- <span class="font-medium">{{ gl.secondReviewer }}</span> -->
                 <input
                  type="text"
                  class="w-48 rounded-md border px-2 py-1 text-sm"
                  placeholder="Input Text"
                />
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>WHT Slip Number</strong></span>
                <!-- <span class="font-medium">{{ gl.whtSlipNumber }}</span> -->
                 <input
                  type="text"
                  class="w-48 rounded-md border px-2 py-1 text-sm"
                  placeholder="Input Text"
                />
              </div>

              <div class="flex justify-between items-center text-sm min-h-[36px]">
                <span class="text-muted-foreground"><strong>Document Type</strong></span>
                <input
                  type="text"
                  class="w-48 rounded-md border px-2 py-1 text-sm"
                  placeholder="Input Text"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- GL vs Recon -->
        <div class="lg:col-span-2 space-y-6">
          <Card>
            <CardContent>
              <div class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- GL -->
                  <div class="space-y-3">
                    <h1 class="text-2xl font-bold tracking-tight text-foreground text-center">G/L</h1>
                  
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Tax Based</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.taxBased) }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>WHT</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.wht) }}</span>
                    </div>
                  </div>

                  <!-- RECON -->
                  <div class="space-y-3">
                    <h1 class="text-2xl font-bold tracking-tight text-foreground text-center">Recon</h1>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Tax Base WHT (Normal)</strong></span>
                      <input
                        type="number"
                        class="w-48 rounded-md border px-2 py-1 text-sm"
                        :value="formatNumber(gl.taxBasedWhtNormal)"
                        disabled
                      />
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>WHT (Normal)</strong></span>
                      <input
                        type="number"
                        class="w-48 rounded-md border px-2 py-1 text-sm"
                        :value="formatNumber(gl.whtNormal)"
                        disabled
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <!-- GL Table -->
                  <DataTableGLItems :data="gl?.glReconItem ?? []" :columns="glReconColumns" />
                </div>
                <!-- See details button -->
                <div class="flex justify-end mt-2">
                  <button
                    @click="showGlDetails = !showGlDetails"
                    class="
                      flex items-center gap-1
                      text-sm font-medium
                      text-foreground
                      underline
                      px-2 py-1
                      rounded-sm
                      hover:bg-muted
                      transition
                    "
                  >
                    {{ showGlDetails ? 'G/L Details ▲' : 'G/L Details ▼' }}
                  </button>
                </div>
                <!-- GL Details -->
                <div 
                  v-if="showGlDetails"
                  class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Left -->
                  <div class="space-y-3">
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>CoCd</strong></span>
                      <span class="font-medium">{{ gl.cocd }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>G/L</strong></span>
                      <span class="font-medium">{{ gl.gl }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Year/Month</strong></span>
                      <span class="font-medium">{{ gl.yearMonth }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Type</strong></span>
                      <span class="font-medium">{{ gl.type }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>User Name</strong></span>
                      <span class="font-medium">{{ gl.username }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Text</strong></span>
                      <span class="font-medium">{{ gl.text }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Clearing Document</strong></span>
                      <span class="font-medium">{{ gl.clearingDocument }}</span>
                    </div>
                  </div>

                  <!-- Right -->
                  <div class="space-y-3">
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Document Currency</strong></span>
                      <span class="font-medium">{{ gl.documentCurrency }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Amount in Document Currency</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.amountInDocumentCurrency) }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Local Currency</strong></span>
                      <span class="font-medium">{{ gl.localCurrency }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Amount in Local Currency</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.amountInLocalCurrency) }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Tax Based</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.taxBased) }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Tax Rate %</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.taxRate*100) }}</span>
                    </div>

                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>WHT</strong></span>
                      <span class="font-medium">{{ formatNumber(gl.wht) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <!-- GL Detail -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Tabs -->
          <div class="flex border-b border-gray-200 mb-4">
            <button
              class="px-4 py-2 font-medium"
              :class="activeTab === 'invoice' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'"
              @click="activeTab = 'invoice'"
            >
              Invoice Detail
            </button>
            <button
              class="px-4 py-2 font-medium"
              :class="activeTab === 'tax' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'"
              @click="activeTab = 'tax'"
            >
              Tax Invoice Detail
            </button>
          </div>

          <!-- Tab Panels -->
          <div>
            <!-- Invoice Detail Tab -->
            <div v-if="activeTab === 'invoice'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- PDF preview -->
              <div class="border rounded-md overflow-hidden h-[500px]">
                <iframe
                  :src= "invoice?.documentUrl"
                  class="w-full h-full"
                  frameborder="0"
                ></iframe>
              </div>

              <!-- Invoice Info + Items -->
              <div v-if="invoice" class="space-y-4 lg:col-span-2">
                <!-- Fields -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Invoice Number</strong></span>
                      <span class="font-medium">{{ invoice?.invoiceNumber }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Invoice Date</strong></span>
                      <span class="font-medium">{{ invoice?.createdAt }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Project Number</strong></span>
                      <span class="font-medium">{{ invoice?.projectNumber }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Currency</strong></span>
                      <span class="font-medium">{{ invoice?.currency }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Sub Total Amount</strong></span>
                      <span class="font-medium">{{ formatNumber(invoice?.subTotalAmount) }}</span>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>VAT %</strong></span>
                      <span class="font-medium">{{ formatNumber(invoice?.vatPercentage) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>VAT Amount</strong></span>
                      <span class="font-medium">{{ formatNumber(invoice?.vatAmount) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>WHT %</strong></span>
                      <span class="font-medium">{{ formatNumber(invoice?.whtPercentage) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>WHT Amount</strong></span>
                      <span class="font-medium">{{ formatNumber(invoice?.whtAmount) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Total Amount</strong></span>
                      <span class="font-medium">{{ formatNumber(invoice?.totalAmount) }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- Invoice Detail Table -->
                <div>
                  <DataTableInvoices :data="invoice?.invoiceDetail ?? []" :columns="invoiceDetailColumns" />
                </div>
              </div>
            </div>

            <!-- Tax Invoice Tab -->
            <div v-if="activeTab === 'tax'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <!-- PDF preview -->
              <div class="border rounded-md overflow-hidden h-[500px]">
                <iframe
                  :src="taxInvoice?.documentUrl"
                  class="w-full h-full"
                  frameborder="0"
                ></iframe>
              </div>

              <!-- Tax Invoice Info + Table -->
              <div class="space-y-4 lg:col-span-2">
                <!-- Fields 1 -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Kode dan Nomor Seri Faktur Pajak</strong></span>
                      <span class="font-medium">{{ taxInvoice?.taxInvoiceNumber }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground font-semibold w-72 shrink-0"><strong>Pengusaha Kena Pajak</strong></span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Nama</strong></span>
                      <span class="font-medium">{{ taxInvoice?.namaPengusahaKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Alamat</strong></span>
                      <span class="font-medium max-w-xs break-words text-right">{{ taxInvoice?.alamatPengusahaKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>NPWP</strong></span>
                      <span class="font-medium">{{ taxInvoice?.npwpPengusahaKenaPajak }}</span>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Tanggal Faktur Pajak</strong></span>
                      <span class="font-medium">{{ taxInvoice?.taxInvoiceDate }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground font-semibold w-72 shrink-0"><strong>Pembelian Barang Kena Pajak/Penerima Jasa Kena Pajak</strong></span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Nama</strong></span>
                      <span class="font-medium">{{ taxInvoice?.namaPembeliKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Alamat</strong></span>
                      <span class="font-medium max-w-xs break-words text-right">{{ taxInvoice?.alamatPembeliKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>NPWP</strong></span>
                      <span class="font-medium">{{ taxInvoice?.npwpPembeliKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>NIK</strong></span>
                      <span class="font-medium">{{ taxInvoice?.nikPembeliKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Nomor Paspor</strong></span>
                      <span class="font-medium">{{ taxInvoice?.nomorPasporPembeliKenaPajak }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm min-h-[36px]">
                      <span class="text-muted-foreground"><strong>Email</strong></span>
                      <span class="font-medium">{{ taxInvoice?.emailPembeliKenaPajak }}</span>
                    </div>
                  </div>
                </div>
                <hr class="border-t border-gray-300 my-4" />
                <!-- Fields 2 -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <div class="flex justify-between items-center text-sm h-12 mb-3">
                      <span class="text-muted-foreground w-48 break-words"><strong>Total Harga Jual / Penggantian / Uang Muka / Termin</strong></span>
                      <span class="font-medium">{{ formatNumber(taxInvoice?.totalTaxBaseWht) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm h-12 mb-3">
                      <span class="text-muted-foreground w-48 break-words"><strong>Dikurangi Potongan Harga</strong></span>
                      <span class="font-medium">{{ formatNumber(taxInvoice?.dikurangiPotonganHarga) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm h-12 mb-3">
                      <span class="text-muted-foreground w-48 break-words"><strong>Dikurangi Uang Muka yang telah diterima</strong></span>
                      <span class="font-medium">{{ formatNumber(taxInvoice?.dikurangiUangMukaYangTelahDiterima) }}</span>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between items-center text-sm h-12 mb-3">
                      <span class="text-muted-foreground w-48 break-words"><strong>Dasar Pengenaan Pajak</strong></span>
                      <span class="font-medium">{{ formatNumber(taxInvoice?.dasarPengenaanPajak) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm h-12 mb-3">
                      <span class="text-muted-foreground w-48 break-words"><strong>Jumlah PPN (Pajak Pertambahan Nilai)</strong></span>
                      <span class="font-medium">{{ formatNumber(taxInvoice?.jumlahPpn) }}</span>
                    </div>
                    <div class="flex justify-between items-center text-sm h-12 mb-3">
                      <span class="text-muted-foreground w-48 break-words"><strong>Jumlah PPnBM (Pajak Penjualan atas Barang Mewah)</strong></span>
                      <span class="font-medium">{{ formatNumber(taxInvoice?.jumlahPpnbm) }}</span>
                    </div>
                  </div>
                </div>
                
                <!-- Tax Invoice Detail Table -->
                <div>
                  <DataTableTaxInvoices :data="taxInvoice?.taxInvoiceDetail ?? []" :columns="taxInvoiceDetailColumns" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div v-else class="min-h-screen flex items-center justify-center bg-muted/40">
    <div class="text-center">
      <h2 class="text-2xl font-bold text-foreground">GL Not Found</h2>
      <p class="text-muted-foreground mt-2">The GL you are looking for does not exist.</p>
      <Button class="mt-4" @click="goBack">Go Back</Button>
    </div>
  </div>
</template>
