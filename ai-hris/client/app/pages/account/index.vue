<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Candidate, LegalDocument, FamilyMember, ResumeDocument, OfferingLetter, LegalDocumentSchemaV2 } from '@/components/candidates/data/schema'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, Save, Upload, FileText, Trash2, Loader2, Plus, AlertTriangle, AlertCircle, CheckCircle2, Info, MoveRight, Edit } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import KartuKeluargaModal from '@/components/candidates/KartuKeluargaModal.vue'
import KartuKeluargaContent from '@/components/candidates/KartuKeluargaContent.vue'
import KtpModal from '@/components/candidates/KtpModal.vue'
import KtpContent from '@/components/candidates/KtpContent.vue'
import OfferingLetterModal from '@/components/candidates/OfferingLetterModal.vue'
import OfferingLetterContent from '@/components/candidates/OfferingLetterContent.vue'
import BukuTabunganModal from '@/components/candidates/BukuTabunganModal.vue'
import BukuTabunganContent from '@/components/candidates/BukuTabunganContent.vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'

const route = useRoute()
const router = useRouter()
const candidateIdCookie = useCookie('candidate_id')
console.log('Candidate ID Cookie:', candidateIdCookie.value)
const candidateId = candidateIdCookie.value || ''

onMounted(() => {
  if (import.meta.client) {
    const isLoggedIn = localStorage.getItem('isLoggedIn')
    if (!isLoggedIn) {
      navigateTo('/account/login')
    }
  }
})

definePageMeta({
  layout: 'blank'
})

// Form state
const form = ref({
  name: '',
  photo_url: '',
  email: '',
  phone: '',
  gender: '',
  date_of_birth: '',
  
  // Address
  address_detail: '',
  address_city: '',
  address_country: '',
  address_zip: undefined as number | undefined,

  position: '',
  experience: 0,
  skills: [] as string[],
  legal_documents: [] as LegalDocument[],
  resume: undefined as ResumeDocument | undefined,
  offering_letter: undefined as OfferingLetter | undefined,
  family_members: [] as FamilyMember[]
})

const newSkill = ref('')
const newFamilyMember = ref({
  name: '',
  relationship: '',
  date_of_birth: '',
  brief_data: {
    occupation: '',
    contact: ''
  }
})
const isUploading = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const isModalOpen = ref(false)
const isFamilyModalOpen = ref(false)
const selectedDocument = ref<LegalDocument | undefined>(undefined)
const showSuccessNotification = ref(false)
const isSaving = ref(false)

const requiredDocuments = ['KTP', 'KK', 'Buku Tabungan', 'Signed Offer Letter']

const documentCompletion = computed(() => {
  // Use form.value to reflect current state including new uploads
  const uploadedTypes = form.value.legal_documents?.map(d => d.type) || []
  
  // Check if offering letter exists
  if (form.value.offering_letter && Object.keys(form.value.offering_letter).length > 0) {
    uploadedTypes.push('Signed Offer Letter')
  }
  
  const missing = requiredDocuments.filter(doc => !uploadedTypes.includes(doc))
  const progress = Math.round(((requiredDocuments.length - missing.length) / requiredDocuments.length) * 100)
  
  return { progress, missing }
})

const discrepancies = computed(() => candidate.value?.discrepancies || [])

// Helper to format date
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch (e) {
    return dateString
  }
}

// Upload State
const isUploadModalOpen = ref(false)
const uploadProgress = ref(0)
const isAnalyzing = ref(false)
const tempUploadedFile = ref<File | null>(null)
const tempExtractedData = ref<any>(null)
const offeringLetterInput = ref<HTMLInputElement | null>(null)
const resumeInput = ref<HTMLInputElement | null>(null)
const currentUploadType = ref<'document' | 'offering_letter' | 'resume'>('document')
const isOfferingLetterModalOpen = ref(false)
const offeringLetterAnalysis = ref<any>(null)

const previewDocument = computed(() => {
  if (!tempExtractedData.value?.data) return null
  const d = tempExtractedData.value.data
  return {
    type: d.type || d.document_type,
    name: d.name,
    url: d.url,
    last_updated: d.last_updated,
    extracted_content: d.document_data || (d.structured_data ? { structured_data: d.structured_data } : undefined)
  } as LegalDocumentSchemaV2
})

const previewOfferingLetter = computed(() => {
  if (!offeringLetterAnalysis.value?.data) return undefined
  
  const d = offeringLetterAnalysis.value.data
  return {
    type: 'Signed Offering Letter',
    name: tempUploadedFile.value?.name || d.name,
    url: d.url,
    last_updated: d.last_updated || new Date().toISOString(),
    extracted_content: {
      content: d.extracted_content?.content || '',
      bounding_boxes: d.extracted_content?.bounding_boxes || [],
      structured_data: d.extracted_content?.structured_data || {}
    }
  } as OfferingLetter
})

const hasResume = computed(() => {
  return form.value.resume !== undefined && form.value.resume !== null && Object.keys(form.value.resume).length > 0
})

const hasOfferingLetter = computed(() => {
  return form.value.offering_letter !== undefined && form.value.offering_letter !== null && Object.keys(form.value.offering_letter).length > 0
})

const uploadDocument = async (file: File) => {
  const formData = new FormData()
  formData.append('document', file)
  formData.append('candidate_id', candidateId)

  try {
    const response = await $fetch('/api/candidates/upload', {
      method: 'POST',
      body: formData,
    })
    return response
  } catch (error) {
    console.error('Upload failed:', error)
    throw new Error('Upload failed')
  }
}

const analyzeOfferingLetter = async (file: File) => {
  const formData = new FormData()
  formData.append('document', file)
  formData.append('candidate_id', candidateId)

  try {
    const response = await $fetch('/api/document/analyze/offering-letter', {
      method: 'POST',
      body: formData,
    })
    console.log('Offering letter analysis response:', response)
    return response
  } catch (error) {
    console.error('Offering letter analysis failed:', error)
    throw new Error('Offering letter analysis failed')
  }
}

const confirmUpload = () => {
    if (!tempUploadedFile.value || !tempExtractedData.value) return

    const result = tempExtractedData.value
    const file = tempUploadedFile.value

    if (currentUploadType.value === 'resume') {
      // Handle resume upload
      const newResume: ResumeDocument = {
        type: 'RESUME',
        name: result.data?.name || file.name,
        url: result.data?.url || '',
        last_updated: result.data?.last_updated || new Date().toISOString(),
        extracted_content: result.data?.document_data || result
      }
      form.value.resume = newResume
    } else if (currentUploadType.value === 'offering_letter') {
      // Handle offering letter upload
      const newOfferingLetter: OfferingLetter = {
        type: 'OFFERING_LETTER',
        name: result.data?.name || file.name,
        url: result.data?.url || '',
        last_updated: result.data?.last_updated || new Date().toISOString(),
        extracted_content: result.data?.document_data || result
      }
      form.value.offering_letter = newOfferingLetter
    } else {
      // Handle legal documents
      let docType = result.data?.document_type || result.data?.type || result.document_type || 'OTHER'

      // Create new document entry
      const newDoc: LegalDocument = {
        type: docType, 
        name: result.data?.name || file.name,
        url: result.data?.url || '', 
        last_updated: result.data?.last_updated || new Date().toISOString(),
        extracted_content: result.data?.document_data || (result.data?.structured_data ? { structured_data: result.data.structured_data } : result)
      }

      form.value.legal_documents.push(newDoc)

      // Auto-fill address if available and empty (only for KK documents)
      if (docType === 'KK' && result.data?.document_data?.structured_data) {
        const sd = result.data.document_data.structured_data
        if (!form.value.address_detail && sd.address) form.value.address_detail = sd.address
        if (!form.value.address_city && sd.city) form.value.address_city = sd.city
        if (!form.value.address_zip && sd.postal_code) form.value.address_zip = parseInt(sd.postal_code.replace(/\D/g, '')) || undefined
      }
    }
    
    isUploadModalOpen.value = false
    tempUploadedFile.value = null
    tempExtractedData.value = null
}

const calculateTotalExperience = (experiences: any[]) => {
  if (!experiences || experiences.length === 0) return 0
  
  let totalMonths = 0
  
  experiences.forEach(exp => {
    const start = new Date(exp.start_date)
    const end = exp.end_date ? new Date(exp.end_date) : new Date()
    
    if (!isNaN(start.getTime()) && !isNaN(end.getTime())) {
      const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth())
      if (months > 0) {
        totalMonths += months
      }
    }
  })
  
  return Number((totalMonths / 12).toFixed(1))
}

// Load data
const { data: candidate, error } = await useFetch<Candidate>(`/api/candidates/${candidateId}`)

if (error.value || !candidate.value) {
  router.push('/account/login')
} else {
  const c = candidate.value
  form.value = {
    name: c.name,
    photo_url: c.photo_url || '',
    email: c.email || '',
    phone: c.phone || '',
    gender: c.gender || '',
    date_of_birth: c.date_of_birth || '',
    
    address_detail: c.address?.detail || '',
    address_city: c.address?.city || '',
    address_country: c.address?.country || '',
    address_zip: c.address?.zip,

    position: c.position || '',
    experience: c.work_experiences ? calculateTotalExperience(c.work_experiences) : (c.experience || 0),
    skills: c.skills || [],
    legal_documents: c.legal_documents || [],
    resume: c.resume,
    offering_letter: c.offering_letter,
    family_members: c.family_members || []
  }
}

const goBack = () => {
  router.back()
}

const addSkill = () => {
  if (newSkill.value.trim() && form.value.skills) {
    if (!form.value.skills.includes(newSkill.value.trim())) {
      form.value.skills.push(newSkill.value.trim())
    }
    newSkill.value = ''
  }
}

const removeSkill = (skill: string) => {
  if (form.value.skills) {
    form.value.skills = form.value.skills.filter(s => s !== skill)
  }
}

const removeDocument = (index: number) => {
  form.value.legal_documents.splice(index, 1)
}

const addFamilyMember = () => {
  if (newFamilyMember.value.name && newFamilyMember.value.relationship) {
    form.value.family_members.push(JSON.parse(JSON.stringify(newFamilyMember.value)))
    // Reset
    newFamilyMember.value = {
      name: '',
      relationship: '',
      date_of_birth: '',
      brief_data: { occupation: '', contact: '' }
    }
    isFamilyModalOpen.value = false
  }
}

const removeFamilyMember = (index: number) => {
  form.value.family_members.splice(index, 1)
}

const openDocumentModal = (doc: LegalDocumentSchemaV2) => {
  selectedDocument.value = doc
  isModalOpen.value = true
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const triggerOfferingLetterUpload = () => {
  offeringLetterInput.value?.click()
}

const triggerResumeUpload = () => {
  resumeInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const file = target.files[0]
  if (!file) return

  currentUploadType.value = 'document'
  tempUploadedFile.value = file
  isUploadModalOpen.value = true
  isAnalyzing.value = true
  uploadProgress.value = 20
  
  try {
    // Upload/analysis
    const result = await uploadDocument(file)
    uploadProgress.value = 100
    tempExtractedData.value = result
  } catch (error) {
    console.error('Upload failed:', error)
    // Handle error (maybe show a toast or message)
    isUploadModalOpen.value = false
  } finally {
    isAnalyzing.value = false
  }
  
  // Reset input so same file can be selected again if needed
  if (fileInput.value) fileInput.value.value = ''
}

const handleOfferingLetterUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const file = target.files[0]
  if (!file) return

  currentUploadType.value = 'offering_letter'
  tempUploadedFile.value = file
  isUploading.value = true
  isAnalyzing.value = true
  uploadProgress.value = 20
  
  try {
    // Analyze offering letter with special API
    const result = await analyzeOfferingLetter(file)
    uploadProgress.value = 100
    offeringLetterAnalysis.value = result
    isOfferingLetterModalOpen.value = true
  } catch (error) {
    console.error('Offering letter analysis failed:', error)
    // Handle error (maybe show a toast or message)
    isOfferingLetterModalOpen.value = false
  } finally {
    isUploading.value = false
    isAnalyzing.value = false
  }
  
  // Reset input so same file can be selected again if needed
  if (offeringLetterInput.value) offeringLetterInput.value.value = ''
}

const handleResumeUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const file = target.files[0]
  if (!file) return

  currentUploadType.value = 'resume'
  tempUploadedFile.value = file
  isUploadModalOpen.value = true
  isAnalyzing.value = true
  uploadProgress.value = 20
  
  try {
    // Upload/analysis
    const result = await uploadDocument(file)
    uploadProgress.value = 100
    tempExtractedData.value = result
  } catch (error) {
    console.error('Upload failed:', error)
    // Handle error (maybe show a toast or message)
    isUploadModalOpen.value = false
  } finally {
    isAnalyzing.value = false
  }
  
  // Reset input so same file can be selected again if needed
  if (resumeInput.value) resumeInput.value.value = ''
}

const confirmOfferingLetter = () => {
  if (!tempUploadedFile.value || !offeringLetterAnalysis.value) return

  const file = tempUploadedFile.value
  const analysis = offeringLetterAnalysis.value
  console.log('Confirmed offering letter analysis:', analysis)

  // Create offering letter entry
  const newOfferingLetter: OfferingLetter = {
    type: 'Signed Offering Letter',
    name: analysis.data?.name || file.name,
    url: analysis.data?.url || '',
    last_updated: analysis.data?.last_updated || new Date().toISOString(),
    extracted_content: {
      content: analysis.data?.extracted_content?.content || '',
      bounding_boxes: analysis.data?.extracted_content?.bounding_boxes || [],
      structured_data: analysis.data?.extracted_content?.structured_data || {}
    }
  }
  
  form.value.offering_letter = newOfferingLetter
  
  // Close modals and reset state
  isOfferingLetterModalOpen.value = false
  tempUploadedFile.value = null
  offeringLetterAnalysis.value = null
}

const saveCandidate = async () => {
  isSaving.value = true
  const payload = {
    name: form.value.name,
    photo_url: form.value.photo_url,
    email: form.value.email,
    phone: form.value.phone,
    phone: form.value.phone,
    gender: form.value.gender,
    date_of_birth: form.value.date_of_birth,
    address: {
      detail: form.value.address_detail,
      city: form.value.address_city,
      country: form.value.address_country,
      zip: form.value.address_zip
    },
    position: form.value.position,
    experience: form.value.experience,
    skills: form.value.skills,
    legal_documents: form.value.legal_documents,
    resume: form.value.resume,
    offering_letter: form.value.offering_letter,
    family_members: form.value.family_members
  }

  try {
    const { data, error } = await useFetch(`/api/candidates/${candidateId}`, {
      method: 'PUT',
      body: payload
    })

    if (error.value) {
      console.error('Error saving candidate:', error.value)
      return
    }

    // Show success notification
    showSuccessNotification.value = true
    
    // Auto-hide notification after 3 seconds
    setTimeout(() => {
      showSuccessNotification.value = false
    }, 3000)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-muted/40 p-6">
    <div class="w-full mx-auto space-y-6">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row gap-6 items-center">
        <div class="relative group">
           <Avatar class="h-24 w-24 border-4 border-background shadow-sm">
              <AvatarImage :src="form.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${form.name}`" class="object-cover" />
              <AvatarFallback>{{ form.name?.charAt(0) }}</AvatarFallback>
           </Avatar>
        </div>
        
        <div class="flex-1 space-y-2">
           <h1 class="text-3xl font-bold tracking-tight text-foreground">{{ form.name }}</h1>
           <div class="flex items-center gap-2 text-muted-foreground">
             <span class="font-medium">{{ form.position }}</span>
             <span v-if="form.email">•</span>
             <span v-if="form.email">{{ form.email }}</span>
           </div>
        </div>
        
        <div class="flex gap-2">
           <Button variant="outline" @click="goBack" :disabled="isSaving">Cancel</Button>
           <Button @click="saveCandidate" :disabled="isSaving">
             <Loader2 v-if="isSaving" class="mr-2 h-4 w-4 animate-spin" />
             <Save v-else class="mr-2 h-4 w-4" />
             {{ isSaving ? 'Saving...' : 'Save Changes' }}
           </Button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Right Column (Sidebar) -->
        <div class="lg:col-span-4 lg:col-start-9 space-y-6 lg:order-2 sticky top-6 self-start">
        <!-- Document Completion Card -->
        <Card :class="{ 'border-blue-600 dark:border-blue-400 shadow-md ring-1 ring-blue-600 dark:ring-blue-400': documentCompletion.progress === 100 }">
          <CardHeader class="pb-3">
            <CardTitle class="text-base font-semibold">Document Completion</CardTitle>
            <CardDescription class="text-xs">
              Please ensure all required documents are uploaded to complete your profile.
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="font-medium">{{ documentCompletion.progress }}% Complete</span>
                <span class="text-muted-foreground">{{ requiredDocuments.length - documentCompletion.missing.length }}/{{ requiredDocuments.length }}</span>
              </div>
              <div class="h-2 bg-muted rounded-full overflow-hidden">
                <div class="h-full bg-blue-600 rounded-full transition-all duration-500" :style="{ width: `${documentCompletion.progress}%` }"></div>
              </div>
            </div>

            <div v-if="documentCompletion.missing.length > 0" class="space-y-2">
              <p class="text-xs font-medium text-muted-foreground">Missing Documents:</p>
              <div class="space-y-1">
                <div v-for="doc in documentCompletion.missing" :key="doc" class="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-500 bg-amber-50 dark:bg-amber-900/20 px-2 py-1.5 rounded border border-amber-100 dark:border-amber-900/30">
                  <AlertCircle class="h-3.5 w-3.5" />
                  <span>{{ doc }}</span>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center gap-2 text-sm text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-1.5 rounded border border-green-100 dark:border-green-900/30">
              <CheckCircle2 class="h-4 w-4" />
              <span>All documents submitted</span>
            </div>
          </CardContent>
        </Card>

        <!-- Discrepancies Warning Card -->
        <Card v-if="discrepancies.length > 0" class="border-amber-200 bg-amber-50/50 dark:bg-amber-950/10">
          <CardHeader class="pb-3">
            <div class="flex items-center justify-between">
              <CardTitle class="text-base font-medium flex items-center gap-2 text-amber-900 dark:text-amber-200">
                <AlertTriangle class="h-5 w-5 text-amber-600" />
                Data Discrepancies
              </CardTitle>
              <Badge variant="outline" class="bg-amber-100 text-amber-700 border-amber-200">
                {{ discrepancies.length }} Issues
              </Badge>
            </div>
            <CardDescription class="text-xs text-amber-800/80 dark:text-amber-200/80 mt-1">
              We found some inconsistencies between your form data and uploaded documents. Please review and correct them.
            </CardDescription>
          </CardHeader>
          <CardContent class="space-y-4 max-h-[300px] overflow-y-auto">
            <div v-for="(discrepancy, index) in discrepancies" :key="index" 
              class="group relative bg-card rounded-lg border shadow-sm overflow-hidden transition-all hover:shadow-md"
            >
              <!-- Severity Strip -->
              <div class="absolute left-0 top-0 bottom-0 w-1.5" :class="{
                'bg-blue-500': discrepancy.severity === 'low',
                'bg-amber-500': discrepancy.severity === 'medium',
                'bg-red-500': discrepancy.severity === 'high'
              }"></div>

              <div class="p-4 pl-5">
                <!-- Header -->
                <div class="flex justify-between items-start mb-3">
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <h4 class="font-semibold text-sm text-foreground">{{ discrepancy.field }}</h4>
                      <Badge v-if="discrepancy.category" variant="secondary" class="text-[10px] px-1.5 h-5 font-medium text-muted-foreground bg-muted">
                        {{ discrepancy.category }}
                      </Badge>
                    </div>
                  </div>
                  <Badge class="capitalize text-[10px] px-2 py-0.5 shadow-none" :class="{
                    'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100': discrepancy.severity === 'low',
                    'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100': discrepancy.severity === 'medium',
                    'bg-red-50 text-red-700 border-red-200 hover:bg-red-100': discrepancy.severity === 'high'
                  }" variant="outline">
                    {{ discrepancy.severity }} Severity
                  </Badge>
                </div>

                <!-- Comparison Box -->
                <div class="grid grid-cols-[1fr_auto_1fr] gap-2 items-center bg-muted/30 rounded-md p-3 mb-3 border border-muted/50">
                  <!-- Target Side (Applicant Data) -->
                  <div class="space-y-1">
                    <div class="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                      <Edit class="h-3 w-3" />
                      {{ discrepancy.target?.type || 'Application' }}
                    </div>
                    <div class="text-sm font-medium text-foreground wrap-break-word">
                      {{ discrepancy.target?.value ?? '-' }}
                    </div>
                  </div>

                  <!-- Arrow -->
                  <div class="text-muted-foreground/40 px-1">
                    <MoveRight class="h-4 w-4" />
                  </div>

                  <!-- Source Side (Document Data) -->
                  <div class="space-y-1 text-right">
                    <div class="flex items-center justify-end gap-1.5 text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
                      {{ discrepancy.source?.type || 'Document' }}
                      <FileText class="h-3 w-3" />
                    </div>
                    <div class="text-sm font-medium text-foreground wrap-break-word">
                      {{ discrepancy.source?.value ?? '-' }}
                    </div>
                  </div>
                </div>

                <!-- Footer Info -->
                <div class="space-y-2">
                  <!-- Note -->
                  <div v-if="discrepancy.note" class="flex gap-2 text-xs text-muted-foreground bg-amber-50/50 dark:bg-amber-900/10 p-2 rounded border border-amber-100 dark:border-amber-900/20">
                    <Info class="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                    <span class="leading-relaxed">{{ discrepancy.note }}</span>
                  </div>

                  <!-- Source -->
                  <div v-if="discrepancy.source?.name" class="flex items-center justify-end">
                    <div class="inline-flex items-center gap-1.5 text-[10px] text-muted-foreground bg-muted/50 px-2 py-1 rounded-full border hover:bg-muted transition-colors cursor-help" :title="discrepancy.source.name">
                      <FileText class="h-3 w-3" />
                      <span class="font-medium truncate max-w-[150px]">
                        {{ discrepancy.source.name }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Left Column (Main Forms) -->
      <div class="lg:col-span-8 lg:row-start-1 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Basic details about the candidate.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="name">Full Name</Label>
              <Input id="name" v-model="form.name" placeholder="John Doe" />
            </div>
            <div class="space-y-2">
              <Label for="email">Email</Label>
              <Input id="email" type="email" v-model="form.email" placeholder="john@example.com" />
            </div>
            <div class="space-y-2">
              <Label for="phone">Phone</Label>
              <Input id="phone" v-model="form.phone" placeholder="+1 234 567 890" />
            </div>
            <div class="space-y-2">
              <Label for="gender">Gender</Label>
              <Select v-model="form.gender">
                <SelectTrigger>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Male">Male</SelectItem>
                  <SelectItem value="Female">Female</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div class="space-y-2">
              <Label for="date_of_birth">Date of Birth</Label>
              <Input id="date_of_birth" type="date" v-model="form.date_of_birth" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Address</CardTitle>
          <CardDescription>Candidate's residence details.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="address_detail">Street Address</Label>
            <Textarea id="address_detail" v-model="form.address_detail" placeholder="123 Main St" />
          </div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="space-y-2">
              <Label for="address_city">City</Label>
              <Input id="address_city" v-model="form.address_city" placeholder="New York" />
            </div>
            <div class="space-y-2">
              <Label for="address_country">Country</Label>
              <Input id="address_country" v-model="form.address_country" placeholder="USA" />
            </div>
            <div class="space-y-2">
              <Label for="address_zip">Zip Code</Label>
              <Input id="address_zip" type="number" v-model="form.address_zip" placeholder="10001" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Family Members</CardTitle>
            <CardDescription>Details about family members.</CardDescription>
          </div>
          <Button size="sm" variant="outline" @click="isFamilyModalOpen = true">
            <Plus class="h-4 w-4 mr-2" />
            Add Member
          </Button>
        </CardHeader>
        <CardContent class="space-y-4">
          <!-- List -->
          <div v-if="form.family_members.length > 0" class="space-y-2">
             <div v-for="(member, index) in form.family_members" :key="index" class="flex items-center justify-between p-3 border rounded-md bg-muted/50">
                <div>
                  <p class="font-medium">{{ member.name }} ({{ member.relationship }})</p>
                  <p class="text-sm text-muted-foreground">
                    DOB: {{ member.date_of_birth || '-' }} | 
                    Job: {{ member.brief_data?.occupation || '-' }} | 
                    Contact: {{ member.brief_data?.contact || '-' }}
                  </p>
                </div>
                <Button variant="ghost" size="icon" @click="removeFamilyMember(index)">
                  <Trash2 class="h-4 w-4 text-destructive" />
                </Button>
             </div>
          </div>
          <div v-else class="text-sm text-muted-foreground text-center py-4 border border-dashed rounded-md">
            No family members listed.
          </div>
        </CardContent>
      </Card>

      <!-- Family Member Modal -->
      <Dialog :open="isFamilyModalOpen" @update:open="isFamilyModalOpen = $event">
        <DialogContent class="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add Family Member</DialogTitle>
            <DialogDescription>
              Add details for a new family member here. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <div class="grid gap-4 py-4">
            <div class="grid grid-cols-4 items-center gap-4">
              <Label for="fm-name" class="text-right">Name</Label>
              <Input id="fm-name" v-model="newFamilyMember.name" class="col-span-3" />
            </div>
            <div class="grid grid-cols-4 items-center gap-4">
              <Label for="fm-rel" class="text-right">Relation</Label>
              <Input id="fm-rel" v-model="newFamilyMember.relationship" class="col-span-3" placeholder="e.g. Spouse" />
            </div>
            <div class="grid grid-cols-4 items-center gap-4">
              <Label for="fm-dob" class="text-right">DOB</Label>
              <Input id="fm-dob" type="date" v-model="newFamilyMember.date_of_birth" class="col-span-3" />
            </div>
            <div class="grid grid-cols-4 items-center gap-4">
              <Label for="fm-job" class="text-right">Job</Label>
              <Input id="fm-job" v-model="newFamilyMember.brief_data.occupation" class="col-span-3" />
            </div>
            <div class="grid grid-cols-4 items-center gap-4">
              <Label for="fm-contact" class="text-right">Contact</Label>
              <Input id="fm-contact" v-model="newFamilyMember.brief_data.contact" class="col-span-3" />
            </div>
          </div>
          <DialogFooter>
            <Button type="submit" @click="addFamilyMember" :disabled="!newFamilyMember.name || !newFamilyMember.relationship">Save changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Card v-if="form.legal_documents.length >= 0">
        <CardHeader>
          <CardTitle>Legal Documents</CardTitle>
          <CardDescription>Manage your legal documents. Ensure all uploads are clear and legible to avoid verification issues.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div v-if="form.legal_documents.length > 0" class="space-y-2">
            <div 
              v-for="(doc, index) in form.legal_documents" 
              :key="index" 
              class="flex items-center justify-between p-3 border rounded-md bg-muted/50 hover:bg-muted cursor-pointer transition-colors"
              @click="openDocumentModal(doc)"
            >
              <div class="flex items-center gap-3 flex-1">
                <FileText class="h-5 w-5 text-muted-foreground" />
                <div class="flex-1">
                  <p class="text-sm font-medium">{{ doc.name }}</p>
                  <p class="text-xs text-muted-foreground">{{ doc.type }} • {{ new Date(doc.last_updated).toLocaleDateString() }}</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" @click.stop="removeDocument(index)" class="text-destructive hover:text-destructive hover:bg-destructive/10">
                <Trash2 class="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div v-else class="text-sm text-muted-foreground text-center py-4 border border-dashed rounded-md">
            No legal documents uploaded yet.
          </div>

          <div class="flex justify-end">
            <input type="file" ref="fileInput" class="hidden" accept=".pdf,.png,.jpg,.jpeg" @change="handleFileUpload" />
            <Button variant="outline" @click="triggerFileUpload" :disabled="isUploading">
              <Loader2 v-if="isUploading" class="mr-2 h-4 w-4 animate-spin" />
              <Upload v-else class="mr-2 h-4 w-4" />
              {{ isUploading ? 'Analyzing...' : 'Upload Legal Document' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Signed Offering Letter</CardTitle>
          <CardDescription>Please upload the signed copy of your offering letter to finalize your acceptance.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div v-if="hasOfferingLetter" class="flex flex-col gap-2 p-4 border rounded-md bg-green-50 hover:bg-green-100 cursor-pointer transition-colors" @click="selectedDocument = form.offering_letter; isModalOpen = true">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3 flex-1">
                <FileText class="h-5 w-5 text-green-600" />
                <div class="flex-1">
                  <div class="flex items-center gap-2">
                    <p class="text-sm font-medium">{{ form.offering_letter.name }}</p>
                    <Badge variant="default" class="bg-green-600">Signed</Badge>
                  </div>
                  <p class="text-xs text-muted-foreground">Signed Offering Letter • {{ new Date(form.offering_letter.last_updated).toLocaleDateString() }}</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" @click.stop="form.offering_letter = undefined" class="text-destructive hover:text-destructive hover:bg-destructive/10">
                <Trash2 class="h-4 w-4" />
              </Button>
            </div>

            <!-- Structured Data Preview -->
            <div v-if="form.offering_letter.extracted_content?.structured_data" class="grid grid-cols-1 sm:grid-cols-3 gap-4 pl-8 mt-1 border-t border-green-200/50 pt-3">
              <div v-if="form.offering_letter.extracted_content.structured_data.position">
                <p class="text-xs text-muted-foreground">Position</p>
                <p class="text-sm font-medium">{{ form.offering_letter.extracted_content.structured_data.position }}</p>
              </div>
              <div v-if="form.offering_letter.extracted_content.structured_data.salary">
                <p class="text-xs text-muted-foreground">Salary</p>
                <p class="text-sm font-medium">{{ form.offering_letter.extracted_content.structured_data.salary }}</p>
              </div>
              <div v-if="form.offering_letter.extracted_content.structured_data.start_date">
                <p class="text-xs text-muted-foreground">Start Date</p>
                <p class="text-sm font-medium">{{ formatDate(form.offering_letter.extracted_content.structured_data.start_date) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="text-sm text-muted-foreground text-center py-4 border border-dashed rounded-md">
            No offering letter uploaded yet.
          </div>

          <div class="flex justify-end">
            <input type="file" ref="offeringLetterInput" class="hidden" accept=".pdf" @change="handleOfferingLetterUpload" />
            <Button variant="outline" @click="triggerOfferingLetterUpload" :disabled="isUploading">
              <Loader2 v-if="isUploading" class="mr-2 h-4 w-4 animate-spin" />
              <Upload v-else class="mr-2 h-4 w-4" />
              {{ isUploading ? 'Analyzing...' : 'Upload Offering Letter' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <KartuKeluargaModal 
        v-if="selectedDocument && (selectedDocument.type === 'KK' || selectedDocument.type === 'KARTU_KELUARGA')"
        :open="isModalOpen" 
        :data="selectedDocument"
        @update:open="isModalOpen = $event"
      />

      <KtpModal 
        v-else-if="selectedDocument && (selectedDocument.type === 'KTP' || selectedDocument.type === 'KARTU_TANDA_PENDUDUK')"
        :open="isModalOpen" 
        :data="selectedDocument"
        @update:open="isModalOpen = $event"
      />

      <OfferingLetterModal 
        v-else-if="selectedDocument && selectedDocument.type === 'Signed Offering Letter'"
        :open="isModalOpen" 
        :data="selectedDocument as any"
        @update:open="isModalOpen = $event"
      />

      <BukuTabunganModal 
        v-else-if="selectedDocument && selectedDocument.type === 'Buku Tabungan'"
        :open="isModalOpen" 
        :data="selectedDocument"
        @update:open="isModalOpen = $event"
      />
      
      <!-- Fallback for other document types -->
      <Dialog 
        v-else-if="selectedDocument"
        :open="isModalOpen" 
        @update:open="isModalOpen = $event"
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{{ selectedDocument.name }}</DialogTitle>
            <DialogDescription>
              Document Type: {{ selectedDocument.type }}
            </DialogDescription>
          </DialogHeader>
          <div class="py-4">
            <p class="text-sm text-muted-foreground mb-2">Raw Content:</p>
            <div class="bg-muted p-4 rounded-md max-h-[300px] overflow-auto">
              <pre class="text-xs whitespace-pre-wrap">{{ selectedDocument.extracted_content?.content || 'No content extracted' }}</pre>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <!-- Upload Analysis Modal -->
      <Dialog :open="isUploadModalOpen" @update:open="isUploadModalOpen = $event">
        <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
          <DialogHeader>
            <DialogTitle>Document Analysis</DialogTitle>
            <DialogDescription>
              {{ isAnalyzing ? 'Analyzing document content...' : 'Review extracted information' }}
            </DialogDescription>
          </DialogHeader>
          
          <div class="flex-1 overflow-hidden py-4">
            <div v-if="isAnalyzing" class="space-y-4 flex flex-col items-center justify-center h-full">
              <Progress :model-value="uploadProgress" class="w-full max-w-md" />
              <p class="text-sm text-center text-muted-foreground">Processing... {{ uploadProgress }}%</p>
            </div>
            
            <KartuKeluargaContent 
              v-else-if="previewDocument && (previewDocument.type === 'KK' || previewDocument.type === 'KARTU_KELUARGA')" 
              :data="previewDocument"
            />

            <KtpContent 
              v-else-if="previewDocument && (previewDocument.type === 'KTP' || previewDocument.type === 'KARTU_TANDA_PENDUDUK')" 
              :data="previewDocument"
            />

            <BukuTabunganContent 
              v-else-if="previewDocument && previewDocument.type === 'Buku Tabungan'" 
              :data="previewDocument"
            />

            <div v-else class="space-y-4">
              <div class="rounded-md bg-muted p-4 max-h-[500px] overflow-y-auto">
                <pre class="text-xs whitespace-pre-wrap">{{ JSON.stringify(tempExtractedData?.data, null, 2) }}</pre>
              </div>
            </div>
          </div>

          <DialogFooter v-if="!isAnalyzing">
            <Button variant="outline" @click="isUploadModalOpen = false">Cancel</Button>
            <Button @click="confirmUpload">Confirm & Add</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <!-- Offering Letter Analysis Modal -->
      <Dialog :open="isOfferingLetterModalOpen" @update:open="isOfferingLetterModalOpen = $event">
        <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
          <DialogHeader>
            <DialogTitle>Offering Letter Preview</DialogTitle>
            <DialogDescription>
              Review the offering letter and signature details
            </DialogDescription>
          </DialogHeader>
          
          <div v-if="isAnalyzing" class="space-y-4 flex flex-col items-center justify-center py-12 h-full">
            <Progress :model-value="uploadProgress" class="w-full max-w-md" />
            <p class="text-sm text-center text-muted-foreground">Analyzing document... {{ uploadProgress }}%</p>
          </div>

          <div v-else-if="previewOfferingLetter" class="flex-1 overflow-hidden py-4">
            <OfferingLetterContent :data="previewOfferingLetter" />
          </div>

          <DialogFooter v-if="!isAnalyzing">
            <Button variant="outline" @click="isOfferingLetterModalOpen = false">Cancel</Button>
            <Button @click="confirmOfferingLetter" :disabled="!previewOfferingLetter?.extracted_content?.structured_data?.is_signed">
              Confirm & Add Offering Letter
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Card>
        <CardHeader>
          <CardTitle>Professional Details</CardTitle>
          <CardDescription>Role, experience, and skills.</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="position">Position</Label>
              <Input id="position" v-model="form.position" placeholder="e.g. Product Designer" />
            </div>
            <div class="space-y-2">
              <Label for="experience">Experience (Years)</Label>
              <Input id="experience" type="number" v-model="form.experience" min="0" />
            </div>
          </div>

          <div class="space-y-2">
            <Label>Skills</Label>
            <div class="flex flex-wrap gap-2 mb-2">
              <Badge v-for="skill in form.skills" :key="skill" variant="secondary" class="gap-1 pr-1">
                {{ skill }}
                <button @click="removeSkill(skill)" class="hover:bg-muted rounded-full p-0.5">
                  <span class="sr-only">Remove</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-x"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                </button>
              </Badge>
            </div>
            <div class="flex gap-2">
              <Input v-model="newSkill" placeholder="Add a skill (e.g. React)" @keydown.enter.prevent="addSkill" />
              <Button type="button" variant="outline" @click="addSkill">Add</Button>
            </div>
          </div>
        </CardContent>
      </Card>
      </div> <!-- End Left Column -->
      </div> <!-- End Grid -->

      <!-- Success Notification -->
      <div 
        v-if="showSuccessNotification"
        class="fixed bottom-6 right-6 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 z-50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
        <span>Data successfully updated!</span>
      </div>

    </div>
  </div>
</template>
