<script setup lang="ts">
import { ref } from 'vue'
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Label } from '@/components/ui/label'
import type { OfferingLetter } from './data/schema'

const props = defineProps<{
  data: OfferingLetter
}>()

const zoom = ref(1)
const minZoom = 1
const maxZoom = 3

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

const zoomIn = () => {
  if (zoom.value < maxZoom) {
    zoom.value = Math.min(zoom.value + 0.2, maxZoom)
  }
}

const zoomOut = () => {
  if (zoom.value > minZoom) {
    zoom.value = Math.max(zoom.value - 0.2, minZoom)
  }
}

const resetZoom = () => {
  zoom.value = minZoom
}
</script>

<template>
  <div class="flex gap-6 flex-1 overflow-hidden h-full">
    <!-- Left Column: Data -->
    <div class="flex flex-col gap-6 flex-1 overflow-auto">
      <!-- Header Info -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 shrink-0">
        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium text-muted-foreground">Position Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-lg font-bold">{{ data.extracted_content?.structured_data?.position || '-' }}</div>
            <div class="text-sm text-muted-foreground mt-1">
              Start Date: {{ formatDate(data.extracted_content?.structured_data?.start_date) }}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium text-muted-foreground">Compensation</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-lg font-bold">{{ data.extracted_content?.structured_data?.salary || '-' }}</div>
            <div class="flex items-center gap-2 mt-1">
              <Badge :variant="data.extracted_content?.structured_data?.is_signed ? 'default' : 'secondary'" :class="data.extracted_content?.structured_data?.is_signed ? 'bg-green-600' : ''">
                {{ data.extracted_content?.structured_data?.is_signed ? 'Signed' : 'Not Signed' }}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Separator class="shrink-0" />

      <!-- Benefits -->
      <div v-if="data.extracted_content?.structured_data?.benefits?.length" class="flex flex-col shrink-0">
        <h3 class="text-lg font-semibold mb-4">Benefits</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div 
            v-for="(benefit, index) in data.extracted_content.structured_data.benefits" 
            :key="index"
            class="p-3 bg-muted/50 rounded-md text-sm"
          >
            {{ benefit }}
          </div>
        </div>
      </div>

      <!-- Full Content -->
      <div class="flex flex-col flex-1 min-h-0">
        <h3 class="text-lg font-semibold mb-4 shrink-0">Document Content</h3>
        <div class="bg-muted p-4 rounded-lg overflow-auto flex-1 border">
          <pre class="text-xs whitespace-pre-wrap text-muted-foreground font-mono">{{ data.extracted_content?.content }}</pre>
        </div>
      </div>
    </div>

    <!-- Right Column: Document Preview -->
    <div class="w-1/3 flex flex-col shrink-0">
      <Card class="h-full flex flex-col">
        <CardHeader class="pb-3 shrink-0">
          <div class="flex items-center justify-between">
            <CardTitle class="text-sm font-medium text-muted-foreground">Document Preview</CardTitle>
          </div>
        </CardHeader>
        <CardContent class="flex-1 overflow-hidden p-0">
          <div v-if="data.url" class="w-full h-full bg-muted rounded-b-lg overflow-hidden">
            <iframe :src="data.url" class="w-full h-full border-0"></iframe>
          </div>
          <div v-else class="flex items-center justify-center h-full text-muted-foreground text-sm p-4">
            No document preview available
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
