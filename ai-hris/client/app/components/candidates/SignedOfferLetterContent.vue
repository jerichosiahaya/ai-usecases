<script setup lang="ts">
import { computed } from 'vue'
import type { OfferingLetter } from '@/components/candidates/data/schema'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, AlertCircle } from 'lucide-vue-next'

interface Props {
  data?: OfferingLetter
}

const props = defineProps<Props>()

const isSigned = computed(() => {
  return props.data?.extracted_content?.structured_data?.exists === true
})

const signedContent = computed(() => {
  return props.data?.extracted_content?.structured_data?.signed_content || 
         props.data?.extracted_content?.content || 
         'No content available'
})
</script>

<template>
  <div v-if="props.data" class="space-y-6 py-4">
    <!-- Signature Status -->
    <div class="flex items-center gap-3 p-4 border rounded-lg" :class="isSigned ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-900/40' : 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-900/40'">
      <div v-if="isSigned" class="flex items-center gap-2 flex-1">
        <CheckCircle2 class="h-5 w-5 text-green-600 dark:text-green-400" />
        <div>
          <p class="font-medium text-green-900 dark:text-green-200">Document Signed</p>
          <p class="text-sm text-green-700 dark:text-green-300">This offering letter has been signed by the candidate</p>
        </div>
      </div>
      <div v-else class="flex items-center gap-2 flex-1">
        <AlertCircle class="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
        <div>
          <p class="font-medium text-yellow-900 dark:text-yellow-200">Awaiting Signature</p>
          <p class="text-sm text-yellow-700 dark:text-yellow-300">This offering letter is pending candidate signature</p>
        </div>
      </div>
      <Badge v-if="isSigned" class="shrink-0 bg-green-100 text-green-700 border-green-200 dark:bg-green-900/40 dark:text-green-300 dark:border-green-900/60">
        Signed
      </Badge>
      <Badge v-else variant="outline" class="shrink-0 border-yellow-200 text-yellow-700 dark:border-yellow-900/60 dark:text-yellow-300">
        Pending
      </Badge>
    </div>

    <!-- Document Content Preview -->
    <div class="space-y-2">
      <label class="text-sm font-medium text-muted-foreground">Document Content</label>
      <div class="bg-muted/50 dark:bg-muted/30 p-4 rounded-lg max-h-[400px] overflow-y-auto border border-border">
        <div class="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
          {{ signedContent }}
        </div>
      </div>
    </div>

    <!-- File Name -->
    <div class="space-y-2">
      <label class="text-sm font-medium text-muted-foreground">File</label>
      <div class="text-sm text-foreground p-3 bg-muted/30 rounded-lg border border-border">
        {{ props.data.name }}
      </div>
    </div>
  </div>
</template>
