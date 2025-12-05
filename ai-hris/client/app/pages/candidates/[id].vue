<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Candidate, KartuKeluargaStructured, LegalDocument } from '@/components/candidates/data/schema'
import KartuKeluargaModal from '@/components/candidates/KartuKeluargaModal.vue'
import OfferingLetterModal from '@/components/candidates/OfferingLetterModal.vue'
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
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const candidateId = route.params.id as string

const { data: candidate, pending: loading, error } = await useFetch<Candidate>(`/api/candidates/${candidateId}`)

const activeTab = ref('notes')

const statusSteps = computed(() => {
  const steps = [
    { value: 'applied', label: 'Applied' },
    { value: 'screening', label: 'Screening' },
    { value: 'interview', label: 'Interview' },
    { value: 'shortlisted', label: 'Shortlisted' },
  ]

  if (candidate.value?.status === 'hired') {
    steps.push({ value: 'hired', label: 'Hired' })
    steps.push({ value: 'onboarding', label: 'Onboarding' })
  } else if (candidate.value?.status === 'rejected') {
    steps.push({ value: 'rejected', label: 'Rejected' })
  } else {
    steps.push({ value: 'decision', label: 'Hired / Rejected' })
  }

  return steps
})

const currentStatusIndex = computed(() => {
  if (!candidate.value?.status) return 0
  const status = candidate.value.status

  if (status === 'hired') return 5
  if (status === 'rejected') return 4

  const index = statusSteps.value.findIndex(s => s.value === status)
  return index !== -1 ? index : 0
})

const activities = computed(() => [
  { title: 'Moved to Interview Stage', date: '2 days ago', description: 'Candidate was moved from Screening to Interview stage.' },
  { title: 'AI Interview Completed', date: '3 days ago', description: 'Candidate completed the AI interview with a score of 8.0/10.' },
  { title: 'Application Received', date: '4 days ago', description: 'Candidate applied for Product Designer I position.' }
])

const formatCurrency = (value: number, currency: string = 'IDR') => {
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: currency, maximumFractionDigits: 0 }).format(value)
}

const formatMarketRange = (range?: { min: number, max: number, currency: string }) => {
  if (!range) return '-'
  return `${formatCurrency(range.min, range.currency)} - ${formatCurrency(range.max, range.currency)}`
}

const getFactorColor = (value: string) => {
  const map: Record<string, string> = {
    'High': 'text-green-600',
    'Very High': 'text-orange-600',
    'Moderate': 'text-blue-600',
    'Low': 'text-red-600',
    'Very Low': 'text-gray-600'
  }
  return map[value] || 'text-foreground'
}

const getSeverityColor = (severity: string) => {
  const map: Record<string, string> = {
    'low': 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-900/20 dark:border-blue-900/40 dark:text-blue-300',
    'medium': 'bg-yellow-50 border-yellow-200 text-yellow-700 dark:bg-yellow-900/20 dark:border-yellow-900/40 dark:text-yellow-300',
    'high': 'bg-red-50 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-900/40 dark:text-red-300'
  }
  return map[severity] || 'bg-gray-50 border-gray-200 text-gray-700'
}

const getSeverityIcon = (severity: string) => {
  const map: Record<string, any> = {
    'low': Info,
    'medium': AlertTriangle,
    'high': AlertCircle
  }
  return map[severity] || Info
}

const requiredDocuments = ['KTP', 'KK', 'Buku Tabungan', 'Signed Offer Letter']

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
  if (!candidate.value) return { progress: 0, missing: [] }

  const uploadedTypes = candidate.value.legal_documents?.map(d => d.type) || []

  // Check if offering letter exists and include it in the count
  if (Object.keys(candidate.value.offering_letter || {}).length > 0) {
    console.log('Offering letter found, adding to uploaded types')
    uploadedTypes.push('Signed Offer Letter')
  }

  const missing = requiredDocuments.filter(doc => !uploadedTypes.includes(doc))
  const progress = Math.round(((requiredDocuments.length - missing.length) / requiredDocuments.length) * 100)

  return { progress, missing }
})

const downloadCV = () => {
  // if (candidate.value?.resume) {
  //   window.open(candidate.value?.resume[0], '_blank')
  // }
  throw new Error('Not implemented yet')
}

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
  if (doc.type === 'KK' && doc.extracted_content) {
    selectedKKData.value = doc
    isKKModalOpen.value = true
  } else if (doc.url) {
    window.open(doc.url, '_blank')
  }
}

const getSignalColor = (signal: string, index?: number) => {
  const colors = [
    'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-900/60',
    'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/40 dark:text-purple-300 dark:border-purple-900/60',
    'bg-pink-100 text-pink-800 border-pink-200 dark:bg-pink-900/40 dark:text-pink-300 dark:border-pink-900/60',
    'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/40 dark:text-red-300 dark:border-red-900/60',
    'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/40 dark:text-green-300 dark:border-green-900/60',
    'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/40 dark:text-yellow-300 dark:border-yellow-900/60',
    'bg-indigo-100 text-indigo-800 border-indigo-200 dark:bg-indigo-900/40 dark:text-indigo-300 dark:border-indigo-900/60',
    'bg-cyan-100 text-cyan-800 border-cyan-200 dark:bg-cyan-900/40 dark:text-cyan-300 dark:border-cyan-900/60',
  ]

  // If index is provided, use it; otherwise use hash-based index
  let colorIndex = 0
  if (index !== undefined) {
    colorIndex = index % colors.length
  } else {
    let hash = 0
    for (let i = 0; i < signal.length; i++) {
      hash = ((hash << 5) - hash) + signal.charCodeAt(i)
      hash = hash & hash
    }
    colorIndex = Math.abs(hash) % colors.length
  }

  return colors[colorIndex]
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
    <div v-else-if="candidate" class="max-w-7xl mx-auto p-6">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column (Main Content) -->
        <div class="lg:col-span-8 space-y-6">

          <!-- Profile Header -->
          <div class="flex flex-col sm:flex-row gap-6 items-start">
            <div class="relative">
              <Avatar class="h-24 w-24 border-4 border-background shadow-sm">
                <AvatarImage
                  :src="candidate?.photo_url ?? `https://api.dicebear.com/7.x/avataaars/svg?seed=${candidate?.name}`"
                  :alt="candidate?.name" class="object-cover" />
                <AvatarFallback>{{ candidate?.name?.charAt(0) }}</AvatarFallback>
              </Avatar>
              <Badge v-if="candidate?.rating"
                class="absolute -bottom-2 -right-2 bg-green-100 text-green-700 hover:bg-green-100 border-green-200 px-2 py-0.5 text-sm font-bold shadow-sm">
                {{ candidate.rating }}/5
              </Badge>
            </div>

            <div class="flex-1 space-y-2">
              <div class="flex justify-between items-start">
                <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                  <h1 class="text-3xl font-bold tracking-tight text-foreground">{{ candidate?.name }}</h1>
                  <span class="text-lg text-muted-foreground">for <span class="inline-block font-semibold">{{
                      candidate?.position }}</span></span>
                </div>
              </div>

              <div class="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <div class="flex items-center gap-1.5">
                  <MapPin class="h-4 w-4" />
                  {{ candidate?.address?.city }}, {{ candidate?.address?.country }}
                </div>

                <div class="flex items-center gap-1.5">
                  <Calendar class="h-4 w-4" />
                  Applied {{ Math.floor((Date.now() - new Date(candidate?.applied_date ?? Date.now()).getTime()) / (1000
                  * 3600 * 24)) }} days ago
                </div>

              </div>

              <!-- Status Stepper -->
              <div class="w-full mt-6">
                <Stepper :model-value="currentStatusIndex" class="flex w-full items-start gap-2">
                  <StepperItem v-for="(step, index) in statusSteps" :key="step.value" :step="index"
                    class="relative flex flex-col flex-1 group" :class="{
                      'items-start': index === 0,
                      'items-center': index !== 0 && index !== statusSteps.length - 1,
                      'items-end': index === statusSteps.length - 1
                    }">
                    <StepperTrigger
                      class="flex flex-col items-center gap-2 p-2 rounded-md hover:bg-muted/50 transition-colors">
                      <StepperIndicator
                        class="h-8 w-8 rounded-full flex items-center justify-center border-2 transition-all duration-300 group-data-[state=active]:bg-primary group-data-[state=active]:border-primary group-data-[state=active]:text-primary-foreground group-data-[state=completed]:bg-primary/20 group-data-[state=completed]:border-primary/20 group-data-[state=completed]:text-primary">
                        <CheckCircle2 v-if="index < currentStatusIndex" class="h-4 w-4" />
                        <span v-else class="text-sm font-medium">{{ index + 1 }}</span>
                      </StepperIndicator>
                      <div class="flex flex-col items-center text-center">
                        <StepperTitle
                          class="text-sm font-medium transition-colors group-data-[state=active]:text-primary group-data-[state=completed]:text-muted-foreground">
                          {{ step.label }}</StepperTitle>
                      </div>
                    </StepperTrigger>
                    <StepperSeparator v-if="index !== statusSteps.length - 1"
                      class="absolute top-6 h-0.5 bg-muted group-data-[state=completed]:bg-primary/20" :class="{
                        'left-[calc(50%+20px)] right-[calc(-50%+20px)]': index !== 0 && index !== statusSteps.length - 2,
                        'left-11 right-[calc(-50%+20px)]': index === 0,
                        'left-[calc(50%+20px)] right-[calc(-100%+44px)]': index === statusSteps.length - 2
                      }" />
                  </StepperItem>
                </Stepper>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-wrap gap-3">
            <Button class="bg-blue-600 hover:bg-blue-700 text-white gap-2">
              <Send class="h-4 w-4" />
              Send Mail
            </Button>
            <Button v-if="candidate?.status === 'hired'" class="bg-green-600 hover:bg-green-700 text-white gap-2"
              @click="router.push(`/candidates/email-payroll/${candidateId}`)">
              <Mail class="h-4 w-4" />
              Email to Payroll
            </Button>
            <Button variant="outline" class="gap-2" @click="router.push(`/candidates/edit/${candidateId}`)">
              <Edit class="h-4 w-4" />
              Edit Profile
            </Button>
            <Button variant="outline" class="gap-2">
              <MoveRight class="h-4 w-4" />
              Move to stage
            </Button>
            <Button variant="outline" class="gap-2" @click="downloadCV">
              <Download class="h-4 w-4" />
              Download Candidate Report
            </Button>
          </div>



          <!-- Signals -->
          <div class="space-y-3">
            <h3 class="text-sm font-semibold text-muted-foreground">Signals</h3>
            <div class="flex flex-wrap gap-3">
              <Badge v-for="(signal, index) in candidate?.interview?.signals" :key="signal" variant="outline"
                :class="getSignalColor(signal, index)" class="p-2">
                {{ signal }}
              </Badge>
            </div>
          </div>

          <!-- AI Interview Summary -->
          <div class="space-y-3">
            <h3 class="text-sm font-semibold text-muted-foreground">AI Interview Summary</h3>
            <p class="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
              {{ candidate?.interview?.summary || 'No summary available.' }}
            </p>
          </div>

          <!-- Score Cards -->
          <div class="space-y-3">
            <h3 class="text-sm font-semibold text-muted-foreground">Score</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <Card v-for="(score, index) in candidate?.interview?.score_details" :key="index"
                class="bg-green-50/50 dark:bg-green-900/10 border-green-100 dark:border-green-900/20">
                <CardContent class="p-4 flex items-center gap-4">
                  <div
                    class="h-10 w-10 rounded-full bg-background flex items-center justify-center shadow-sm text-green-600 dark:text-green-400">
                    <Headphones class="h-5 w-5" />
                  </div>
                  <div>
                    <div class="text-2xl font-bold text-foreground">{{ score.value.toFixed(1) }}</div>
                    <div class="text-xs font-medium text-muted-foreground">{{ score.label }}</div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          <!-- AI Interview Score Details -->
          <Card v-if="candidate?.interview?.interview_scores">
            <CardHeader class="pb-3">
              <CardTitle class="text-base font-medium">AI Interview Score</CardTitle>
            </CardHeader>
            <CardContent class="space-y-6">
              <div v-for="score in candidate.interview.interview_scores" :key="score.label">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm font-medium text-muted-foreground">{{ score.label }}</span>
                  <span class="text-sm font-bold text-foreground">{{ score.value }}</span>
                </div>
                <div class="w-full bg-muted rounded-full h-2">
                  <div class="h-2 rounded-full transition-all duration-500 bg-green-500"
                    :style="{ width: `${(score.value / 10) * 100}%` }" />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Salary Analysis Card -->
          <Card v-if="candidate?.salary">
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-base font-medium flex items-center gap-2">
                  <Banknote class="h-4 w-4 text-muted-foreground" />
                  Salary & Market Analysis
                </CardTitle>
                <Badge variant="outline" class="bg-green-50 text-green-700 border-green-200">
                  {{ candidate.salary.status }}
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div class="space-y-1">
                  <span class="text-xs text-muted-foreground">Candidate Expectation</span>
                  <div class="font-bold text-lg">{{ formatCurrency(candidate.salary.expectation) }}</div>
                </div>
                <div class="space-y-1">
                  <span class="text-xs text-muted-foreground">Market Range</span>
                  <div class="font-bold text-lg text-muted-foreground">{{
                    formatMarketRange(candidate.salary.market_range) }}</div>
                </div>
              </div>

              <div class="bg-muted/30 rounded-lg p-3 space-y-2">
                <div class="flex items-center gap-2 text-sm font-medium">
                  <Sparkles class="h-4 w-4 text-purple-500" />
                  AI Analysis
                </div>
                <p class="text-sm text-muted-foreground leading-relaxed">
                  {{ candidate.salary.analysis }}
                </p>
              </div>

              <div class="grid grid-cols-3 gap-2 pt-2">
                <div v-for="factor in candidate.salary.factors" :key="factor.name"
                  class="text-center p-2 border rounded-md bg-background">
                  <div class="text-xs text-muted-foreground mb-1">{{ factor.name }}</div>
                  <div class="font-medium text-sm" :class="getFactorColor(factor.value)">{{ factor.value }}</div>
                </div>
              </div>
            </CardContent>
          </Card>



          <!-- Contact Info -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground">Contact Info</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Name</span>
                <span class="font-medium text-right">{{ candidate?.name }}</span>
              </div>
              <Separator />
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Phone</span>
                <span class="font-medium text-right">{{ candidate?.phone || '-' }}</span>
              </div>
              <Separator />
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Email</span>
                <span class="font-medium text-right truncate text-blue-600">{{ candidate?.email }}</span>
              </div>
              <Separator />
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Gender</span>
                <span class="font-medium text-right">{{ candidate?.gender || '-' }}</span>
              </div>
              <Separator />
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Birthday</span>
                <span class="font-medium text-right" v-if="candidate?.date_of_birth">{{
                  formatDate(candidate.date_of_birth) }} ({{ calculateAge(candidate.date_of_birth) }} years old)</span>
                <span v-else class="font-medium text-right text-muted-foreground">-</span>
              </div>
              <Separator />
              <div class="grid grid-cols-[80px_1fr] gap-2 text-sm">
                <span class="text-muted-foreground">Address</span>
                <div class="text-right">
                  <div class="font-medium">{{ candidate?.address?.detail || '-' }}</div>
                  <div class="text-muted-foreground text-xs">
                    {{ [candidate?.address?.city, candidate?.address?.country,
                    candidate?.address?.zip].filter(Boolean).join(', ') }}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Family Members -->
          <Card v-if="candidate?.family_members && candidate.family_members.length > 0">
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Users class="h-4 w-4" />
                Family Members
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(member, i) in candidate.family_members" :key="i" class="border rounded-lg p-3 bg-muted/30">
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
              </div>
            </CardContent>
          </Card>

          <!-- Experience -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Briefcase class="h-4 w-4" />
                Experience
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(exp, i) in candidate?.work_experiences" :key="i"
                class="border rounded-lg p-4 bg-linear-to-br from-purple-50/50 to-transparent dark:from-purple-950/20 hover:shadow-sm transition-all">
                <div class="space-y-3">
                  <!-- Top row: Position and Duration -->
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
                      })() }}
                    </Badge>
                  </div>

                  <!-- Company -->
                  <div>
                    <div class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Company</div>
                    <div class="text-sm text-foreground font-medium mt-1">{{ exp.company }}</div>
                  </div>

                  <!-- Duration -->
                  <div class="pt-2 border-t border-border">
                    <div class="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock class="h-3.5 w-3.5" />
                      <span>{{ formatDate(exp.start_date) }} - {{ exp.end_date ? formatDate(exp.end_date) : 'Present'
                        }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Education -->
          <Card>
            <CardHeader class="">
              <CardTitle class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <GraduationCap class="h-4 w-4" />
                Education
              </CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="(edu, i) in candidate?.education" :key="i"
                class="border rounded-lg p-4 bg-linear-to-br from-blue-50/50 to-transparent dark:from-blue-950/20 hover:shadow-sm transition-all">
                <div class="space-y-3">
                  <!-- Top row: Degree and Graduation Year -->
                  <div class="flex items-start justify-between gap-3">
                    <div class="flex-1">
                      <div class="font-semibold text-sm text-foreground">{{ edu.degree }}</div>
                    </div>
                    <Badge
                      class="bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300 dark:border-blue-900/60 shrink-0">
                      {{ edu.graduation_year }}
                    </Badge>
                  </div>

                  <!-- Institution -->
                  <div>
                    <div class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Institution</div>
                    <div class="text-sm text-foreground font-medium mt-1">{{ edu.institution }}</div>
                  </div>

                  <!-- Field of Study -->
                  <div>
                    <div class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Field of Study</div>
                    <div class="text-sm text-foreground mt-1">{{ edu.field_of_study }}</div>
                  </div>

                  <!-- GPA -->
                  <div class="pt-2 border-t border-border">
                    <div class="flex items-center justify-between">
                      <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">GPA</span>
                      <div
                        class="bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300 px-2.5 py-1 rounded font-bold text-sm">
                        {{ edu.gpa }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Resume -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground">Résumé</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="border rounded-lg p-3 flex items-center justify-between bg-muted/50">
                <div class="flex items-center gap-3 overflow-hidden">
                  <div class="h-8 w-8 bg-background rounded border flex items-center justify-center shrink-0">
                    <FileText class="h-4 w-4 text-red-500" />
                  </div>
                  <div class="flex flex-col overflow-hidden">
                    <span class="text-sm font-medium truncate">resume_{{ candidate.name.toLowerCase().split(' ')[0]
                      }}.pdf</span>
                    <span class="text-xs text-muted-foreground">PDF Document</span>
                  </div>
                </div>
                <Button variant="ghost" size="icon" class="h-8 w-8" @click="downloadCV">
                  <ExternalLink class="h-4 w-4 text-muted-foreground" />
                </Button>
              </div>

              <!-- Resume Preview Image (Mock) -->
              <div
                class="mt-3 border rounded-lg overflow-hidden bg-background h-32 flex items-center justify-center relative group cursor-pointer"
                @click="downloadCV">
                <div class="absolute inset-0 bg-muted/30 flex flex-col items-center justify-center p-4">
                  <div
                    class="w-full h-full bg-background shadow-sm p-2 text-[6px] text-muted-foreground overflow-hidden">
                    <div class="font-bold text-foreground text-[8px] mb-1">{{ candidate.name }}</div>
                    <div class="mb-1">PRODUCT DESIGNER</div>
                    <div class="space-y-1">
                      <div class="h-1 bg-muted w-full"></div>
                      <div class="h-1 bg-muted w-3/4"></div>
                      <div class="h-1 bg-muted w-5/6"></div>
                      <div class="h-1 bg-muted w-full"></div>
                      <div class="h-1 bg-muted w-1/2"></div>
                    </div>
                  </div>
                </div>
                <div
                  class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors flex items-center justify-center">
                  <ExternalLink
                    class="h-6 w-6 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- Signed Offering Letter -->
          <Card v-if="Object.keys(candidate?.offering_letter || {}).length > 0">
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
          </Card>

          <!-- Legal Documents -->
          <Card>
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground">Legal Documents</CardTitle>
            </CardHeader>
            <CardContent class="space-y-3">
              <div v-for="doc in candidate?.legal_documents" :key="doc.type"
                class="border rounded-lg p-3 flex items-center justify-between bg-muted/50 cursor-pointer hover:bg-muted/80 transition-colors"
                @click="handleDocumentClick(doc)">
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
            </CardContent>
          </Card>
        </div>

        <!-- Right Column (Sidebar) -->
        <div class="lg:col-span-4 space-y-6">

          <!-- Document Completion Card -->
          <Card v-if="candidate?.status === 'hired'"
            :class="{ 'border-blue-600 dark:border-blue-400 shadow-md ring-1 ring-blue-600 dark:ring-blue-400': candidate?.status === 'hired' }">
            <CardHeader class="pb-3">
              <CardTitle class="text-sm font-medium text-muted-foreground">Document Completion</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="font-medium">{{ documentCompletion.progress }}% Complete</span>
                  <span class="text-muted-foreground">{{ candidate?.legal_documents?.length }}/{{
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
          <Card v-if="candidate?.discrepancies && candidate.discrepancies.length > 0"
            class="border-amber-200 bg-amber-50/50 dark:bg-amber-950/10">
            <CardHeader class="pb-3">
              <div class="flex items-center justify-between">
                <CardTitle class="text-base font-medium flex items-center gap-2 text-amber-900 dark:text-amber-200">
                  <AlertTriangle class="h-5 w-5 text-amber-600" />
                  Data Discrepancies
                </CardTitle>
                <Badge variant="outline" class="bg-amber-100 text-amber-700 border-amber-200">
                  {{ candidate.discrepancies.length }} Issues
                </Badge>
              </div>
            </CardHeader>
            <CardContent class="space-y-4">
              <div v-for="(discrepancy, index) in candidate.discrepancies" :key="index"
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
          <div class="bg-muted/20 rounded-lg border p-1 flex gap-1">
            <Button variant="ghost" size="sm" class="flex-1 transition-all"
              :class="activeTab === 'notes' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
              @click="activeTab = 'notes'">
              <MessageSquare class="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" class="flex-1 transition-all"
              :class="activeTab === 'activity' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'"
              @click="activeTab = 'activity'">
              <Activity class="h-4 w-4" />
            </Button>
          </div>

          <!-- Notes Tab Content -->
          <div v-if="activeTab === 'notes'" class="space-y-4">
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Internal Notes</CardTitle>
              </CardHeader>
              <CardContent class="space-y-4">
                <div v-for="(note, i) in candidate?.notes" :key="i" class="flex gap-3">
                  <Avatar class="h-8 w-8 border">
                    <AvatarFallback class="text-xs">{{ note.author.charAt(0) }}</AvatarFallback>
                  </Avatar>
                  <div class="flex-1 space-y-1">
                    <div class="flex items-center justify-between">
                      <span class="text-sm font-medium">{{ note.author }}</span>
                      <!-- <span class="text-xs text-muted-foreground">{{ note. }}</span> -->
                    </div>
                    <p class="text-xs text-muted-foreground">{{ note.role }}</p>
                    <p class="text-sm text-foreground bg-muted/50 p-2 rounded-md mt-1">{{ note.message }}</p>
                  </div>
                </div>

                <div class="pt-2">
                  <Button variant="outline" class="w-full text-xs h-8">Add Note</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- Activity Tab Content -->
          <div v-else-if="activeTab === 'activity'" class="space-y-4">
            <Card>
              <CardHeader class="pb-3">
                <CardTitle class="text-sm font-medium text-muted-foreground">Activity Log</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="ml-2 border-l border-border space-y-8 my-2">
                  <div v-for="(activity, i) in activities" :key="i" class="relative pl-6">
                    <span
                      class="absolute -left-[6.5px] top-1.5 h-3 w-3 rounded-full bg-primary ring-4 ring-background"></span>
                    <div class="flex flex-col gap-1">
                      <div class="flex items-center justify-between">
                        <span class="text-sm font-medium text-foreground">{{ activity.title }}</span>
                        <span class="text-xs text-muted-foreground">{{ activity.date }}</span>
                      </div>
                      <p class="text-sm text-muted-foreground">{{ activity.description }}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

        </div>
      </div>
    </div>

    <!-- Modals -->
    <KartuKeluargaModal v-model:open="isKKModalOpen" :data="selectedKKData" />

    <!-- Signed Offering Letter Modal -->
    <OfferingLetterModal 
      :open="isOfferingLetterModalOpen" 
      :data="candidate?.offering_letter"
      @update:open="isOfferingLetterModalOpen = $event"
    />
  </div>
</template>
