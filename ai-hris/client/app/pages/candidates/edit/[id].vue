<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Candidate, LegalDocument, FamilyMember } from '@/components/candidates/data/schema'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, Save, Upload, FileText, Trash2, Loader2, Plus } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import KartuKeluargaModal from '@/components/candidates/KartuKeluargaModal.vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'

const route = useRoute()
const router = useRouter()
const candidateId = route.params.id as string

// Form state
const form = ref({
  name: '',
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
  router.push('/candidates')
} else {
  const c = candidate.value
  form.value = {
    name: c.name,
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

const openDocumentModal = (doc: LegalDocument) => {
  console.log('Opening document:', doc)
  selectedDocument.value = doc
  isModalOpen.value = true
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const file = target.files[0]
  if (!file) return

  isUploading.value = true

  try {
    const formData = new FormData()
    formData.append('document', file)

    const { data, error } = await useFetch('/api/document/analyze', {
      method: 'POST',
      body: formData
    })

    if (error.value) {
      console.error('Error analyzing document:', error.value)
      // You might want to show a toast notification here
      return
    }

    const result = data.value as any // Type this properly if possible

    // Create new document entry
    const newDoc: LegalDocument = {
      type: 'KARTU_KELUARGA', // Assuming KK for now based on endpoint usage
      name: file.name,
      url: '', // No URL yet
      last_updated: new Date().toISOString(),
      extracted_content: result.data
    }

    form.value.legal_documents.push(newDoc)

    // Auto-fill address if available and empty
    if (result.data?.structured_data) {
      const sd = result.data.structured_data
      if (!form.value.address_detail && sd.address) form.value.address_detail = sd.address
      if (!form.value.address_city && sd.city) form.value.address_city = sd.city
      if (!form.value.address_zip && sd.postal_code) form.value.address_zip = parseInt(sd.postal_code.replace(/\D/g, '')) || undefined
      // Province/District could be mapped if we had fields for them
    }

  } catch (e) {
    console.error('Upload failed:', e)
  } finally {
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const saveCandidate = () => {
  // Here you would typically make an API call to save the data
  console.log('Saving candidate:', form.value)
  
  // For now, just navigate back
  router.push(`/candidates/${candidateId}`)
}
</script>

<template>
  <div class="min-h-screen bg-muted/40 p-6">
    <div class="w-full mx-auto space-y-6">
      
      <!-- Header -->
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" @click="goBack">
          <ArrowLeft class="h-5 w-5" />
        </Button>
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-foreground">Edit Candidate</h1>
          <p class="text-muted-foreground">Update candidate information</p>
        </div>
      </div>

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
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
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

      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
          <CardDescription>Manage legal documents (e.g. Kartu Keluarga).</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div v-if="form.legal_documents.length > 0" class="space-y-2">
            <div 
              v-for="(doc, index) in form.legal_documents" 
              :key="index" 
              class="flex items-center justify-between p-3 border rounded-md bg-muted/50 hover:bg-muted cursor-pointer transition-colors"
              @click="openDocumentModal(doc)"
            >
              <div class="flex items-center gap-3">
                <FileText class="h-5 w-5 text-muted-foreground" />
                <div>
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
            No documents uploaded yet.
          </div>

          <div class="flex justify-end">
            <input type="file" ref="fileInput" class="hidden" accept=".pdf,.png,.jpg,.jpeg" @change="handleFileUpload" />
            <Button variant="outline" @click="triggerFileUpload" :disabled="isUploading">
              <Loader2 v-if="isUploading" class="mr-2 h-4 w-4 animate-spin" />
              <Upload v-else class="mr-2 h-4 w-4" />
              {{ isUploading ? 'Analyzing...' : 'Upload Document' }}
            </Button>
          </div>
        </CardContent>
      </Card>

      <KartuKeluargaModal 
        v-if="selectedDocument"
        :open="isModalOpen" 
        :data="selectedDocument"
        @update:open="isModalOpen = $event"
      />

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

      <div class="flex justify-end gap-4">
        <Button variant="outline" @click="goBack">Cancel</Button>
        <Button @click="saveCandidate">
          <Save class="mr-2 h-4 w-4" />
          Save Changes
        </Button>
      </div>

    </div>
  </div>
</template>
