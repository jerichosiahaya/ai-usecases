<script setup lang="ts">
import { ref, watch } from 'vue'
import { CheckCircle2, AlertCircle, FileText } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import type { OfferingLetter } from './data/schema'

const props = defineProps<{
  data: OfferingLetter
}>()

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

const isSigned = ref(props.data.extracted_content?.structured_data?.is_signed)

watch(() => props.data.extracted_content?.structured_data?.is_signed, (newVal) => {
  isSigned.value = newVal
})

const markAsUnsigned = () => {
  isSigned.value = false
}
</script>

<template>
  <div class="flex flex-col gap-6 h-full overflow-hidden">
    <!-- Signature Status Banner -->
    <div 
      class="flex items-center gap-3 p-4 rounded-lg border shrink-0"
      :class="isSigned ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-100 border-red-200 text-red-700'"
    >
      <CheckCircle2 v-if="isSigned" class="h-6 w-6" />
      <AlertCircle v-else class="h-6 w-6" />
      <div class="flex-1">
        <h3 class="font-semibold">{{ isSigned ? 'Document Signed' : 'Document Not Signed' }}</h3>
        <p class="text-sm opacity-90">
          {{ isSigned ? 'This offering letter has been digitally signed by the candidate.' : 'This offering letter has not been signed by the candidate.' }}
        </p>
      </div>
      <Button 
        v-if="isSigned"
        variant="outline" 
        size="sm"
        class="bg-white/50 hover:bg-white/80 border-green-300 text-green-800 hover:text-green-900"
        @click="markAsUnsigned"
      >
        Mark as Unsigned
      </Button>
    </div>

    <div class="flex gap-6 flex-1 overflow-hidden">
      <!-- Left Column: Structured Data -->
      <div class="flex flex-col gap-6 w-1/3 overflow-y-auto pr-2">
        <Card>
          <CardHeader>
            <CardTitle class="text-base">Key Details</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div>
              <p class="text-sm text-muted-foreground">Position</p>
              <p class="font-medium">{{ data.extracted_content?.structured_data?.position || '-' }}</p>
            </div>
            
            <Separator />
            
            <div>
              <p class="text-sm text-muted-foreground">Start Date</p>
              <p class="font-medium">{{ formatDate(data.extracted_content?.structured_data?.start_date) }}</p>
            </div>

            <Separator />

            <div>
              <p class="text-sm text-muted-foreground">Salary</p>
              <p class="font-medium">{{ data.extracted_content?.structured_data?.salary || '-' }}</p>
            </div>
          </CardContent>
        </Card>

        <Card v-if="data.extracted_content?.structured_data?.benefits?.length">
          <CardHeader>
            <CardTitle class="text-base">Benefits</CardTitle>
          </CardHeader>
          <CardContent>
            <ul class="space-y-2">
              <li 
                v-for="(benefit, index) in data.extracted_content.structured_data.benefits" 
                :key="index"
                class="text-sm flex items-start gap-2"
              >
                <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                <span>{{ benefit }}</span>
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-base">Extracted Content</CardTitle>
          </CardHeader>
          <CardContent class="text-sm whitespace-pre-wrap">
            <div v-if="data.extracted_content?.content">
              {{ data.extracted_content.content }}
            </div>
            <div v-else class="text-muted-foreground">
              <FileText class="inline h-4 w-4 mr-1 mb-1" />
              No extracted content available.
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Column: Document Content (Text) -->
      <div class="flex flex-col flex-1 min-w-0 h-full">
        <ClientOnly>
          <CandidatesOfferingLetterPdfViewer :url="data.url" />
        </ClientOnly>
      </div>
    </div>
  </div>
</template>
