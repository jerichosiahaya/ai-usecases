<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Candidate } from '@/components/candidates/data/schema'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { ArrowLeft, Send, CheckCircle2, Paperclip } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const candidateId = route.params.id as string

const { data: candidate, pending: loading, error } = await useFetch<Candidate>(`/api/candidates/${candidateId}`)

const emailTo = ref('ssc-payroll@company.com')
const emailSubject = computed(() => `New Employee: ${candidate.value?.name} - ${candidate.value?.position}`)
const emailBody = ref('')
const selectedDocuments = ref<string[]>([])

// Initialize email body once candidate is loaded
watch(candidate, (newVal) => {
  if (newVal) {
    emailBody.value = `Dear SSC Payroll Team,

Please be informed that we have hired a new employee.

Name: ${newVal.name}
Position: ${newVal.position}
Email: ${newVal.email}
Phone: ${newVal.phone || 'N/A'}
Address: ${newVal.address?.city}, ${newVal.address?.country}

Please proceed with the payroll setup.

Regards,
HR Team`

    // Initialize selected documents with all available legal documents
    if (newVal.legal_documents) {
      selectedDocuments.value = newVal.legal_documents.map(doc => doc.name)
    }
  }
}, { immediate: true })

const isSending = ref(false)
const isSent = ref(false)

const handleSend = async () => {
  isSending.value = true
  // Mock sending email
  await new Promise(resolve => setTimeout(resolve, 1500))
  isSending.value = false
  isSent.value = true
  
  // Redirect back after a delay
  setTimeout(() => {
    router.push(`/candidates/${candidateId}`)
  }, 2000)
}

const goBack = () => {
  router.push(`/candidates/${candidateId}`)
}
</script>

<template>
  <div class="bg-muted/40 p-6">
    <div class="w-full mx-auto space-y-6">
      <!-- Header -->
      <div class="flex items-center gap-4">
        <Button variant="outline" size="icon" @click="goBack">
          <ArrowLeft class="h-4 w-4" />
        </Button>
        <h1 class="text-2xl font-bold tracking-tight">Email to Payroll</h1>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-6 bg-red-50 border border-red-200 rounded-lg text-red-700">
        Failed to load candidate details.
      </div>

      <!-- Email Form -->
      <Card v-else>
        <CardHeader>
          <CardTitle>Draft Email</CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="to">To</Label>
            <Input id="to" v-model="emailTo" readonly />
          </div>
          
          <div class="space-y-2">
            <Label for="subject">Subject</Label>
            <Input id="subject" :model-value="emailSubject" readonly />
          </div>
          
          <div class="space-y-2">
            <Label for="body">Message</Label>
            <Textarea 
              id="body" 
              v-model="emailBody" 
              class="min-h-[300px] font-mono text-sm"
            />
          </div>

          <div class="space-y-2">
            <Label>Attachments</Label>
            <div class="border rounded-md p-4 space-y-3 bg-background">
              <div v-if="!candidate?.legal_documents?.length" class="text-sm text-muted-foreground italic">
                No legal documents available.
              </div>
              <div v-else v-for="doc in candidate.legal_documents" :key="doc.name" class="flex items-center space-x-2">
                <Checkbox 
                  :id="doc.name" 
                  :checked="selectedDocuments.includes(doc.name)"
                  @update:checked="(checked) => {
                    if (checked) {
                      selectedDocuments.push(doc.name)
                    } else {
                      selectedDocuments = selectedDocuments.filter(d => d !== doc.name)
                    }
                  }"
                />
                <Label :for="doc.name" class="flex items-center gap-2 cursor-pointer font-normal">
                  <Paperclip class="h-4 w-4 text-muted-foreground" />
                  <span>{{ doc.name }}</span>
                  <span class="text-xs text-muted-foreground">({{ doc.type }})</span>
                </Label>
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter class="flex justify-end gap-3">
          <Button variant="outline" @click="goBack" :disabled="isSending || isSent">
            Cancel
          </Button>
          <Button @click="handleSend" :disabled="isSending || isSent" class="min-w-[120px]">
            <div v-if="isSending" class="flex items-center gap-2">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
              Sending...
            </div>
            <div v-else-if="isSent" class="flex items-center gap-2">
              <CheckCircle2 class="h-4 w-4" />
              Sent
            </div>
            <div v-else class="flex items-center gap-2">
              <Send class="h-4 w-4" />
              Send Email
            </div>
          </Button>
        </CardFooter>
      </Card>
    </div>
  </div>
</template>
