<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Employee, KartuKeluargaStructured, LegalDocument } from '@/components/candidates/data/schema'
import KartuKeluargaModal from '@/components/candidates/KartuKeluargaModal.vue'
import SignedOfferLetterContent from '@/components/candidates/SignedOfferLetterContent.vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import {
  Stepper,
  StepperDescription,
  StepperIndicator,
  StepperItem,
  StepperSeparator,
  StepperTitle,
  StepperTrigger,
} from '@/components/ui/stepper'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Send,
  MoveRight,
  Download,
  AlertTriangle,
  MapPin,
  Clock,
  Calendar,
  Headphones,
  Gem,
  FileText,
  Info,
  MessageSquare,
  Activity,
  ExternalLink,
  Briefcase,
  CreditCard,
  Users,
  GraduationCap,
  IdCard,
  Edit,
  AlertCircle,
  CheckCircle2,
  Banknote,
  Shield,
  Mail,
  Sparkles,
  AlertTriangleIcon,
  SquareUser,
  Plus,
  X,
  Trash2,
  Folders
} from 'lucide-vue-next'

interface UploadResponse {
  url: string
  success: boolean
}

definePageMeta({
  layout: "blank"
})

const route = useRoute()
const router = useRouter()
const employeeId = route.params.id as string


const { data: employeeData, pending: loading, error } = await useFetch<Employee[]>(`/api/employees/${employeeId}`)

const employee = employeeData.value?.[0]


const activeTab = ref('notes')


const activities = computed(() => [
  { title: 'Moved to Interview Stage', date: '2 days ago', description: 'Candidate was moved from Screening to Interview stage.' },
  { title: 'AI Interview Completed', date: '3 days ago', description: 'Candidate completed the AI interview with a score of 8.0/10.' },
  { title: 'Application Received', date: '4 days ago', description: 'Candidate applied for Product Designer I position.' }
])



// Edit mode state
const isEditMode = ref(false)

// File upload refs
const fileInputRefs = ref<Record<number, HTMLInputElement>>({})

// Editable form data
const editForm = ref({
  name: employee?.name || '',
  phone: employee?.phone || '',
  email: employee?.email || '',
  gender: employee?.gender || '',
  date_of_birth: employee?.date_of_birth || '',
  address: {
    detail: employee?.address?.detail || '',
    city: employee?.address?.city || '',
    country: employee?.address?.country || '',
    zip: employee?.address?.zip || ''
  },
  family_members: employee?.family_members ? JSON.parse(JSON.stringify(employee.family_members)) : [],
  work_experiences: employee?.work_experiences ? JSON.parse(JSON.stringify(employee.work_experiences)) : [],
  education: employee?.education ? JSON.parse(JSON.stringify(employee.education)) : [],
  legalDocuments: employee?.legalDocuments ? JSON.parse(JSON.stringify(employee.legalDocuments)) : []
})

// Reset form when toggling edit mode
const toggleEditMode = () => {
  if (isEditMode.value) {
    // Cancelled editing, reset form
    editForm.value = {
      name: employee?.name || '',
      phone: employee?.phone || '',
      email: employee?.email || '',
      gender: employee?.gender || '',
      date_of_birth: employee?.date_of_birth || '',
      address: {
        detail: employee?.address?.detail || '',
        city: employee?.address?.city || '',
        country: employee?.address?.country || '',
        zip: employee?.address?.zip || ''
      },
      family_members: employee?.family_members ? JSON.parse(JSON.stringify(employee.family_members)) : [],
      work_experiences: employee?.work_experiences ? JSON.parse(JSON.stringify(employee.work_experiences)) : [],
      education: employee?.education ? JSON.parse(JSON.stringify(employee.education)) : [],
      legalDocuments: employee?.legalDocuments ? JSON.parse(JSON.stringify(employee.legalDocuments)) : []
    }
  }
  isEditMode.value = !isEditMode.value
}

// Helper function for opening documents
const openDocumentInNewTab = (url: string) => {
  if (typeof window !== 'undefined') {
    window.open(url, '_blank')
  }
}

// Legal Documents functions
const addLegalDocument = () => {
  editForm.value.legalDocuments.push({
    name: '',
    type: '',
    url: '',
    extracted_content: null,
    last_updated: new Date().toISOString()
  })
}

const removeLegalDocument = (index: number) => {
  editForm.value.legalDocuments.splice(index, 1)
}

const handleFileUpload = async (event: Event, index: number) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) return

  try {
    // Create FormData for file upload
    const formData = new FormData()
    formData.append('file', file)
    formData.append('employeeId', employeeId)
    formData.append('documentType', editForm.value.legalDocuments[index].type)

    // Upload file to server with typed response
    const response = await $fetch<UploadResponse>('/api/v1/hr/document/upload', {
      method: 'POST',
      body: formData
    })

    // Update document with uploaded file info
    editForm.value.legalDocuments[index].name = file.name
    editForm.value.legalDocuments[index].url = response.url
    editForm.value.legalDocuments[index].last_updated = new Date().toISOString()

    console.log('File uploaded successfully:', response)
  } catch (error) {
    console.error('Failed to upload file:', error)
    // Show error message to user
  }
}

const triggerFileInput = (index: number) => {
  fileInputRefs.value[index]?.click()
}

// Document type options
const documentTypes = [
  'KTP',
  'KK',
  'Ijazah',
  'Buku Tabungan',
  'NPWP',
  'Resume',
  'Signed Offer Letter',
  'Other'
]

// Family Members functions
const addFamilyMember = () => {
  editForm.value.family_members.push({
    name: '',
    relationship: '',
    date_of_birth: '',
    brief_data: {
      occupation: '',
      contact: ''
    }
  })
}

const removeFamilyMember = (index: number) => {
  editForm.value.family_members.splice(index, 1)
}

// Work Experience functions
const addWorkExperience = () => {
  editForm.value.work_experiences.push({
    position: '',
    company: '',
    start_date: '',
    end_date: null,
    is_current: false,
    description: ''
  })
}

const removeWorkExperience = (index: number) => {
  editForm.value.work_experiences.splice(index, 1)
}

// Education functions
const addEducation = () => {
  editForm.value.education.push({
    degree: '',
    institution: '',
    field_of_study: '',
    graduation_year: new Date().getFullYear(),
    gpa: 0
  })
}

const removeEducation = (index: number) => {
  editForm.value.education.splice(index, 1)
}

// Save changes
const saveChanges = async () => {
  try {
    // Here you would make an API call to update the employee
    const response = await $fetch(`/api/employees/${employeeId}`, {
      method: 'PATCH',
      body: editForm.value
    })

    // Update local data
    if (employee) {
      Object.assign(employee, editForm.value)
    }

    // Exit edit mode
    isEditMode.value = false

    // Show success message
    console.log('Changes saved successfully!')
  } catch (error) {
    console.error('Failed to save changes:', error)
  }
}
const requiredDocuments = ['KTP', 'KK', 'Ijazah', 'Buku Tabungan', 'Signed Offer Letter']

const getDocumentIcon = (docType: string) => {
  const iconMap: Record<string, any> = {
    'KTP': IdCard,
    'KARTU_KELUARGA': Users,
    'KK': Users,
    'IJAZAH': GraduationCap,
    'Ijazah': GraduationCap,
    'BUKU_TABUNGAN': CreditCard,
    'Buku Tabungan': CreditCard,
    'NPWP': FileText,
    'RESUME': FileText,
    'Resume': FileText,
    'Signed Offer Letter': FileText,
    'OFFERING_LETTER': FileText,
  }
  return iconMap[docType] || FileText
}

const documentCompletion = computed(() => {
  if (!employee) return { progress: 0, missing: [] }

  const uploadedTypes = employee?.legalDocuments?.map((d: any) => d.type) || []

  // Check if offering letter exists and include it in the count
  // if (Object.keys(employee?.value.offering_letter || {}).length > 0) {
  //   console.log('Offering letter found, adding to uploaded types')
  //   uploadedTypes.push('Signed Offer Letter')
  // }

  const missing = requiredDocuments.filter(doc => !uploadedTypes.includes(doc))
  const progress = Math.round(((requiredDocuments.length - missing.length) / requiredDocuments.length) * 100)

  return { progress, missing }
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
}

const calculateAge = (dateString: string) => {
  const today = new Date()
  const birthDate = new Date(dateString)
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }

  return age
}

const isKKModalOpen = ref(false)
const selectedKKData = ref<LegalDocument | undefined>(undefined)
const isOfferingLetterModalOpen = ref(false)

const handleDocumentClick = (doc: any) => {
  console.log('Document clicked:', doc)
  if (doc.type === 'KK' && doc.extractedContent) {
    selectedKKData.value = doc
    isKKModalOpen.value = true
  } else if (doc.url) {
    window.open(doc.url, '_blank')
  }
}

</script>

<template>
  <div class="min-h-screen bg-muted/40">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-7xl mx-auto p-6">
      <Card class="bg-red-50 border-red-200">
        <CardContent class="pt-6">
          <div class="flex items-center gap-2 text-red-700">
            <AlertCircle class="h-5 w-5" />
            <span>Failed to load candidate details. Please try again.</span>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Content -->
    <div v-else-if="employee" class="max-w-7xl mx-auto p-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column (Main Content) -->
        <div class="lg:col-span-8 space-y-6">

          <!-- Profile Header -->
          <div class="flex flex-col sm:flex-row gap-6 items-start">
            <div class="relative">
              <Avatar class="h-24 w-24 border-4 border-background shadow-sm">
                <AvatarImage
                  :src="employee?.photo_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(employee?.name || 'user')}`"
                  :alt="employee?.name" class="object-cover" />
                <AvatarFallback>{{ employee?.name?.charAt(0) || 'U' }}</AvatarFallback>
              </Avatar>
              <Badge v-if="employee?.rating"
                class="absolute -bottom-2 -right-2 bg-green-100 text-green-700 hover:bg-green-100 border-green-200 px-2 py-0.5 text-sm font-bold shadow-sm">
                {{ employee.rating }}/5
              </Badge>
            </div>

            <div class="flex-1 space-y-2">
              <div class="flex justify-between items-start">
                <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                  <h1 class="text-3xl font-bold tracking-tight text-foreground">{{ employee?.name }}</h1>
                  <span class="text-lg text-muted-foreground">for <span class="inline-block font-semibold">{{
                    employee?.position }}</span></span>
                </div>
              </div>

              <div class="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <div class="flex items-center gap-1.5">
                  <MapPin class="h-4 w-4" />
                  {{ employee?.address?.city }}, {{ employee?.address?.country }}
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-wrap gap-3">
            <Button v-if="!isEditMode" variant="outline" class="gap-2" @click="toggleEditMode">
              <Edit class="h-4 w-4" />
              Edit Profile
            </Button>

            <template v-else>
              <Button class="gap-2 bg-green-600 hover:bg-green-700 text-white" @click="saveChanges">
                <CheckCircle2 class="h-4 w-4" />
                Save Changes
              </Button>
              <Button variant="outline" class="gap-2" @click="toggleEditMode">
                <X class="h-4 w-4" />
                Cancel
              </Button>
            </template>
          </div>

          <!-- Contact Info -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <SquareUser class="w-4 h-4" />
                  Contact Information
                </CardTitle>
                <Badge v-if="isEditMode" variant="outline" class="bg-blue-50 text-blue-700 border-blue-200">
                  Editing
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-4">

              <!-- Name -->
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm items-center">
                <span class="text-muted-foreground">Name</span>
                <span v-if="!isEditMode" class="font-medium text-right">{{ employee?.name }}</span>
                <input v-else v-model="editForm.name" type="text"
                  class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Enter name" />
              </div>
              <Separator />

              <!-- Phone -->
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm items-center">
                <span class="text-muted-foreground">Phone</span>
                <span v-if="!isEditMode" class="font-medium text-right">{{ employee?.phone || '-' }}</span>
                <input v-else v-model="editForm.phone" type="tel"
                  class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Enter phone number" />
              </div>
              <Separator />

              <!-- Email -->
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm items-center">
                <span class="text-muted-foreground">Email</span>
                <span v-if="!isEditMode" class="font-medium text-right truncate text-blue-600">{{ employee?.email
                }}</span>
                <input v-else v-model="editForm.email" type="email"
                  class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Enter email" />
              </div>
              <Separator />

              <!-- Gender -->
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm items-center">
                <span class="text-muted-foreground">Gender</span>
                <span v-if="!isEditMode" class="font-medium text-right">{{ employee?.gender || '-' }}</span>
                <select v-else v-model="editForm.gender"
                  class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary">
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <Separator />

              <!-- Birthday -->
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm items-center">
                <span class="text-muted-foreground">Birthday</span>
                <span v-if="!isEditMode" class="font-medium text-right">
                  <template v-if="employee?.date_of_birth">
                    {{ formatDate(employee.date_of_birth) }} ({{ calculateAge(employee.date_of_birth) }} years old)
                  </template>
                  <template v-else>-</template>
                </span>
                <input v-else v-model="editForm.date_of_birth" type="date"
                  class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <Separator />

              <!-- Address -->
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Address</span>
                <div v-if="!isEditMode" class="text-right">
                  <div class="font-medium">{{ employee?.address?.detail || '-' }}</div>
                  <div class="text-muted-foreground text-xs">
                    {{ [employee?.address?.city, employee?.address?.country,
                    employee?.address?.zip].filter(Boolean).join(', ') }}
                  </div>
                </div>
                <div v-else class="space-y-2">
                  <input v-model="editForm.address.detail" type="text"
                    class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="Street address" />
                  <div class="grid grid-cols-3 gap-2">
                    <input v-model="editForm.address.city" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="City" />
                    <input v-model="editForm.address.country" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="Country" />
                    <input v-model="editForm.address.zip" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="ZIP" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>



          <!-- Family Members -->
          <Card v-if="(employee?.family_members && employee.family_members.length > 0) || isEditMode">
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Users class="h-4 w-4" />
                  Family Members
                </CardTitle>
                <Button v-if="isEditMode" variant="outline" size="sm" class="gap-2" @click="addFamilyMember">
                  <Plus class="h-4 w-4" />
                  Add Member
                </Button>
              </div>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(member, i) in (isEditMode ? editForm.family_members : employee.family_members)" :key="i"
                class="border rounded-lg p-3 bg-muted/30 relative">
                <!-- Delete Button (Edit Mode) -->
                <Button v-if="isEditMode" variant="ghost" size="icon"
                  class="absolute top-2 right-2 h-6 w-6 text-red-500 hover:text-red-700 hover:bg-red-50"
                  @click="removeFamilyMember(i)">
                  <Trash2 class="h-4 w-4" />
                </Button>

                <template v-if="!isEditMode">
                  <div class="flex justify-between items-start">
                    <div>
                      <div class="font-medium text-sm">{{ member.name }}</div>
                      <div class="text-xs text-muted-foreground">{{ member.relationship }}</div>
                    </div>
                    <div v-if="member.date_of_birth" class="text-xs text-muted-foreground">
                      {{ formatDate(member.date_of_birth) }}
                    </div>
                  </div>
                  <div v-if="member.brief_data" class="mt-2 text-xs text-muted-foreground grid grid-cols-2 gap-2">
                    <div>
                      <span v-if="member.brief_data.occupation">
                        <span class="font-semibold">Occupation:</span> {{ member.brief_data.occupation }}
                      </span>
                    </div>
                    <div class="text-right">
                      <span v-if="member.brief_data.contact">
                        <span class="font-semibold">Contact:</span> {{ member.brief_data.contact }}
                      </span>
                    </div>
                  </div>
                </template>

                <!-- Edit Mode -->
                <template v-else>
                  <div class="space-y-3 pr-8">
                    <div class="grid grid-cols-2 gap-2">
                      <input v-model="member.name" type="text"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Name" />
                      <input v-model="member.relationship" type="text"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Relationship" />
                    </div>
                    <input v-model="member.date_of_birth" type="date"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Date of Birth" />
                    <div class="grid grid-cols-2 gap-2">
                      <input v-model="member.brief_data.occupation" type="text"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Occupation" />
                      <input v-model="member.brief_data.contact" type="text"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Contact" />
                    </div>
                  </div>
                </template>
              </div>
            </CardContent>
          </Card>

          <!-- Experience -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Briefcase class="h-4 w-4" />
                  Experience
                </CardTitle>
                <Button v-if="isEditMode" variant="outline" size="sm" class="gap-2" @click="addWorkExperience">
                  <Plus class="h-4 w-4" />
                  Add Experience
                </Button>
              </div>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(exp, i) in (isEditMode ? editForm.work_experiences : employee?.work_experiences)" :key="i"
                class="border rounded-lg p-4 bg-linear-to-br from-purple-50/50 to-transparent dark:from-purple-950/20 hover:shadow-sm transition-all relative">
                <!-- Delete Button (Edit Mode) -->
                <Button v-if="isEditMode" variant="ghost" size="icon"
                  class="absolute top-2 right-2 h-6 w-6 text-red-500 hover:text-red-700 hover:bg-red-50"
                  @click="removeWorkExperience(i)">
                  <Trash2 class="h-4 w-4" />
                </Button>

                <template v-if="!isEditMode">
                  <div class="space-y-3">
                    <div class="flex items-start justify-between gap-3">
                      <div class="flex-1">
                        <div class="font-semibold text-sm text-foreground">{{ exp.position }}</div>
                      </div>
                      <Badge
                        class="bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-900/40 dark:text-purple-300 dark:border-purple-900/60 shrink-0 text-xs">
                        {{(() => {
                          const totalMonths = Math.ceil((new Date(exp.end_date || new Date()).getTime() - new
                            Date(exp.start_date).getTime()) / (1000 * 60 * 60 * 24 * 30.44))
                          const years = Math.floor(totalMonths / 12)
                          const months = totalMonths % 12
                          return years > 0 ? `${years} year${years > 1 ? 's' : ''} ${months} month${months !== 1 ? 's' :
                            ''}` : `${months} month${months !== 1 ? 's' : ''}`
                        })()}}
                      </Badge>
                    </div>
                    <div>
                      <div class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Company</div>
                      <div class="text-sm text-foreground font-medium mt-1">{{ exp.company }}</div>
                    </div>
                    <div class="pt-2 border-t border-border">
                      <div class="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock class="h-3.5 w-3.5" />
                        <span>{{ formatDate(exp.start_date) }} - {{ exp.end_date ? formatDate(exp.end_date) : 'Present'
                        }}</span>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- Edit Mode -->
                <template v-else>
                  <div class="space-y-3 pr-8">
                    <input v-model="exp.position" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Position" />
                    <input v-model="exp.company" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Company" />
                    <div class="grid grid-cols-2 gap-2">
                      <div>
                        <label class="text-xs text-muted-foreground">Start Date</label>
                        <input v-model="exp.start_date" type="date"
                          class="w-full px-3 py-2 text-sm border rounded-md bg-background" />
                      </div>
                      <div>
                        <label class="text-xs text-muted-foreground">End Date</label>
                        <input v-model="exp.end_date" type="date"
                          class="w-full px-3 py-2 text-sm border rounded-md bg-background" :disabled="exp.is_current" />
                      </div>
                    </div>
                    <!-- <div class="flex items-center gap-2">
                      <input v-model="exp.is_current" type="checkbox" class="h-4 w-4"
                        @change="if (exp.is_current) exp.end_date = null" />
                      <label class="text-sm">Currently working here</label>
                    </div> -->
                    <textarea v-model="exp.description" rows="2"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background"
                      placeholder="Description (optional)" />
                  </div>
                </template>
              </div>
            </CardContent>
          </Card>

          <!-- Education -->
          <Card>
            <CardHeader>
              <div class="flex items-center justify-between">
                <CardTitle class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <GraduationCap class="h-4 w-4" />
                  Education
                </CardTitle>
                <Button v-if="isEditMode" variant="outline" size="sm" class="gap-2" @click="addEducation">
                  <Plus class="h-4 w-4" />
                  Add Education
                </Button>
              </div>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(edu, i) in (isEditMode ? editForm.education : employee?.education)" :key="i"
                class="border rounded-lg p-4 bg-linear-to-br from-blue-50/50 to-transparent dark:from-blue-950/20 hover:shadow-sm transition-all relative">
                <!-- Delete Button (Edit Mode) -->
                <Button v-if="isEditMode" variant="ghost" size="icon"
                  class="absolute top-2 right-2 h-6 w-6 text-red-500 hover:text-red-700 hover:bg-red-50"
                  @click="removeEducation(i)">
                  <Trash2 class="h-4 w-4" />
                </Button>

                <template v-if="!isEditMode">
                  <div class="space-y-3">
                    <div class="flex items-start justify-between gap-3">
                      <div class="flex-1">
                        <div class="font-semibold text-sm text-foreground">{{ edu.degree }}</div>
                      </div>
                      <Badge
                        class="bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-900/60 shrink-0">
                        {{ edu.graduation_year }}
                      </Badge>
                    </div>
                    <div>
                      <div class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Institution</div>
                      <div class="text-sm text-foreground font-medium mt-1">{{ edu.institution }}</div>
                    </div>
                    <div>
                      <div class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Field of Study
                      </div>
                      <div class="text-sm text-foreground mt-1">{{ edu.field_of_study }}</div>
                    </div>
                    <div class="pt-2 border-t border-border">
                      <div class="flex items-center justify-between">
                        <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">GPA</span>
                        <div
                          class="bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300 px-2.5 py-1 rounded font-bold text-sm">
                          {{ edu.gpa }}
                        </div>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- Edit Mode -->
                <template v-else>
                  <div class="space-y-3 pr-8">
                    <input v-model="edu.degree" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Degree" />
                    <input v-model="edu.institution" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Institution" />
                    <input v-model="edu.field_of_study" type="text"
                      class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="Field of Study" />
                    <div class="grid grid-cols-2 gap-2">
                      <input v-model="edu.graduation_year" type="number"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background"
                        placeholder="Graduation Year" />
                      <input v-model="edu.gpa" type="number" step="0.01" min="0" max="4"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background" placeholder="GPA" />
                    </div>
                  </div>
                </template>
              </div>
            </CardContent>
          </Card>

          <!-- Legal Documents -->
          <Card>
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  <Folders class="w-4 h-4" />
                  Legal Documents
                </CardTitle>
                <Button v-if="isEditMode" variant="outline" size="sm" class="gap-2" @click="addLegalDocument">
                  <Plus class="h-4 w-4" />
                  Add Document
                </Button>
              </div>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(doc, i) in (isEditMode ? editForm.legalDocuments : employee?.legalDocuments)" :key="i"
                class="border rounded-lg p-3 bg-muted/50 relative"
                :class="{ 'cursor-pointer hover:bg-muted/80 transition-colors': !isEditMode }"
                @click="!isEditMode && handleDocumentClick(doc)">
                <!-- Delete Button (Edit Mode) -->
                <Button v-if="isEditMode" variant="ghost" size="icon"
                  class="absolute top-2 right-2 h-6 w-6 text-red-500 hover:text-red-700 hover:bg-red-50 z-10"
                  @click.stop="removeLegalDocument(i)">
                  <Trash2 class="h-4 w-4" />
                </Button>

                <template v-if="!isEditMode">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3 overflow-hidden">
                      <div class="h-8 w-8 bg-background rounded border flex items-center justify-center shrink-0">
                        <component :is="getDocumentIcon(doc.type)" class="h-4 w-4 text-blue-500" />
                      </div>
                      <div class="flex flex-col overflow-hidden">
                        <span class="text-sm font-medium truncate">{{ doc.name }}</span>
                        <span class="text-xs text-muted-foreground">{{ doc.type }}</span>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" class="h-8 w-8" @click.stop="handleDocumentClick(doc)">
                      <ExternalLink class="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </div>
                </template>

                <!-- Edit Mode -->
                <template v-else>
                  <div class="space-y-3 pr-8">
                    <!-- Document Type Dropdown -->
                    <div>
                      <label class="text-xs text-muted-foreground">Document Type</label>
                      <select v-model="doc.type"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary">
                        <option value="">Select document type</option>
                        <option v-for="type in documentTypes" :key="type" :value="type">
                          {{ type }}
                        </option>
                      </select>
                    </div>

                    <!-- Document Name -->
                    <div>
                      <label class="text-xs text-muted-foreground">Document Name</label>
                      <input v-model="doc.name" type="text"
                        class="w-full px-3 py-2 text-sm border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="Document name" readonly />
                    </div>

                    <!-- File Upload -->
                    <div>
                      <label class="text-xs text-muted-foreground">Upload File</label>
                      <div class="flex gap-2">
                        <input :ref="el => { if (el) fileInputRefs[i] = el as HTMLInputElement }" type="file"
                          class="hidden" accept=".pdf,.jpg,.jpeg,.png" @change="handleFileUpload($event, i)" />
                        <Button variant="outline" size="sm" class="gap-2 flex-1" @click.stop="triggerFileInput(i)">
                          <Upload class="h-4 w-4" />
                          {{ doc.url ? 'Change File' : 'Upload File' }}
                        </Button>
                        <Button v-if="doc.url" variant="outline" size="sm" class="gap-2"
                          @click.stop="openDocumentInNewTab(doc.url)">
                          <ExternalLink class="h-4 w-4" />
                          View
                        </Button>
                      </div>
                      <p v-if="doc.url" class="text-xs text-muted-foreground mt-1 truncate">
                        Current: {{ doc.name }}
                      </p>
                    </div>

                    <!-- Last Updated -->
                    <div v-if="doc.last_updated" class="text-xs text-muted-foreground">
                      Last updated: {{ new Date(doc.last_updated).toLocaleDateString() }}
                    </div>
                  </div>
                </template>
              </div>

              <!-- Empty State -->
              <div v-if="(!employee?.legalDocuments || employee.legalDocuments.length === 0) && !isEditMode"
                class="text-center py-8 text-muted-foreground">
                <Folders class="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p class="text-sm">No legal documents uploaded</p>
              </div>
            </CardContent>
          </Card>


        </div>


        <!-- Signed Offering Letter -->
        <!-- <Card v-if="Object.keys(employee?.offering_letter || {}).length > 0">
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground">Signed Offering Letter</CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div
                class="border rounded-lg p-3 flex items-center justify-between bg-muted/50 cursor-pointer hover:bg-muted/80 transition-colors"
                @click="isOfferingLetterModalOpen = true">
                <div class="flex items-center gap-3 overflow-hidden">
                  <div class="h-8 w-8 bg-background rounded border flex items-center justify-center shrink-0">
                    <component :is="getDocumentIcon('Signed Offer Letter')" class="h-4 w-4 text-green-500" />
                  </div>
                  <div class="flex flex-col overflow-hidden">
                    <span class="text-sm font-medium truncate">{{ candidate.offering_letter?.name }}</span>
                    <span class="text-xs text-muted-foreground">{{ candidate.offering_letter?.type }}</span>
                  </div>
                </div>
                <Button variant="ghost" size="icon" class="h-8 w-8" @click.stop="isOfferingLetterModalOpen = true">
                  <ExternalLink class="h-4 w-4 text-muted-foreground" />
                </Button>
              </div>
            </CardContent>
          </Card> -->

        <!-- Legal Documents -->



        <!-- Right Column (Sidebar) -->
        <div class="lg:col-span-4 space-y-6">

          <!-- Document Completion Card -->
          <Card v-if="employee?.status === 'active'"
            :class="{ 'border-blue-600 dark:border-blue-400 shadow-md ring-1 ring-blue-600 dark:ring-blue-400': employee?.status === 'active' }">
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground">Document Completion</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="font-medium">{{ documentCompletion.progress }}% Complete</span>
                  <span class="text-muted-foreground">{{ employee?.legalDocuments?.length }}/{{
                    requiredDocuments.length }}</span>
                </div>
                <div class="h-2 bg-muted rounded-full overflow-hidden">
                  <div class="h-full bg-blue-600 rounded-full transition-all duration-500"
                    :style="{ width: `${documentCompletion.progress}%` }"></div>
                </div>
              </div>

              <div v-if="documentCompletion.missing.length > 0" class="space-y-2">
                <p class="text-xs font-medium text-muted-foreground">Missing Documents:</p>
                <div class="space-y-1">
                  <div v-for="doc in documentCompletion.missing" :key="doc"
                    class="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-500 bg-amber-50 dark:bg-amber-900/20 px-2 py-1.5 rounded border border-amber-100 dark:border-amber-900/30">
                    <AlertCircle class="h-3.5 w-3.5" />
                    <span>{{ doc }}</span>
                  </div>
                </div>
              </div>
              <div v-else
                class="flex items-center gap-2 text-sm text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-1.5 rounded border border-green-100 dark:border-green-900/30">
                <CheckCircle2 class="h-4 w-4" />
                <span>All documents submitted</span>
              </div>
            </CardContent>
          </Card>

          <!-- Discrepancies Warning Card -->
          <Card v-if="employee?.discrepancies && employee.discrepancies.length > 0"
            class="border-amber-200 bg-amber-50/50 dark:bg-amber-950/10">
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-base font-medium flex items-center gap-2 text-amber-900 dark:text-amber-200">
                  <AlertTriangle class="h-5 w-5 text-amber-600" />
                  Data Discrepancies
                </CardTitle>
                <Badge variant="outline" class="bg-amber-100 text-amber-700 border-amber-200">
                  {{ employee.discrepancies.length }} Issues
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-4">
              <div v-for="(discrepancy, index) in employee.discrepancies" :key="index"
                class="group relative bg-card rounded-lg border shadow-sm overflow-hidden transition-all hover:shadow-md">
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
                        <Badge v-if="discrepancy.category" variant="secondary"
                          class="text-[10px] px-1.5 h-5 font-medium text-muted-foreground bg-muted">
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
                  <div
                    class="grid grid-cols-[1fr_auto_1fr] gap-2 items-center bg-muted/30 rounded-md p-3 mb-3 border border-muted/50">
                    <!-- Target Side (Applicant Data) -->
                    <div class="space-y-1">
                      <div
                        class="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
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
                      <div
                        class="flex items-center justify-end gap-1.5 text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">
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
                    <div v-if="discrepancy.note"
                      class="flex gap-2 text-xs text-muted-foreground bg-amber-50/50 dark:bg-amber-900/10 p-2 rounded border border-amber-100 dark:border-amber-900/20">
                      <Info class="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                      <span class="leading-relaxed">{{ discrepancy.note }}</span>
                    </div>

                    <!-- Source -->
                    <div v-if="discrepancy.source?.name" class="flex items-center justify-end">
                      <div
                        class="inline-flex items-center gap-1.5 text-[10px] text-muted-foreground bg-muted/50 px-2 py-1 rounded-full border hover:bg-muted transition-colors cursor-help"
                        :title="discrepancy.source.name">
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

          <!-- Tabs -->

          <!-- Notes Tab Content -->

          <!-- Activity Tab Content -->


        </div>
      </div>
    </div>

    <!-- Modals -->
    <KartuKeluargaModal v-model:open="isKKModalOpen" :data="selectedKKData" />

    <!-- Signed Offering Letter Modal -->
    <!-- <Dialog :open="isOfferingLetterModalOpen" @update:open="isOfferingLetterModalOpen = $event">
      <DialogContent class="w-[95vw] max-w-2xl flex flex-col p-6 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Signed Offering Letter</DialogTitle>
          <DialogDescription>
            Review the signed offering letter document
          </DialogDescription>
        </DialogHeader>

        <SignedOfferLetterContent :data="employee?.offering_letter" />
      </DialogContent>
    </Dialog> -->
  </div>
</template>
