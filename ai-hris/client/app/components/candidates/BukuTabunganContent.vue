<script setup lang="ts">
import { ref } from 'vue'
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-vue-next'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import type { BukuTabungan } from './data/schema'

const props = defineProps<{
  data: BukuTabungan
}>()

const imageRef = ref<HTMLImageElement | null>(null)
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
            <CardTitle class="text-sm font-medium text-muted-foreground">Account Holder</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-lg font-bold">{{ data.extracted_content?.structured_data?.account_holder_name }}</div>
            <div class="text-sm text-muted-foreground">{{ data.extracted_content?.structured_data?.account_type || 'Account' }}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader class="pb-2">
            <CardTitle class="text-sm font-medium text-muted-foreground">Bank Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="text-sm font-medium">{{ data.extracted_content?.structured_data?.bank_name }}</div>
            <div class="text-sm text-muted-foreground">Branch: {{ data.extracted_content?.structured_data?.branch_name }}</div>
          </CardContent>
        </Card>
      </div>

      <Separator class="shrink-0" />

      <!-- Account Details -->
      <div class="flex flex-col gap-4 shrink-0">
        <h3 class="text-lg font-semibold">Account Details</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">Account Number</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="text-base font-mono font-semibold">{{ data.extracted_content?.structured_data?.account_number || '-' }}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">Document Last Updated</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="text-base">{{ formatDate(data.last_updated) }}</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>

    <!-- Right Column: Document Preview -->
    <div class="w-1/3 flex flex-col shrink-0">
      <Card class="h-full flex flex-col">
        <CardHeader class="pb-3 shrink-0">
          <div class="flex items-center justify-between">
            <CardTitle class="text-sm font-medium text-muted-foreground">Document Preview</CardTitle>
            <div class="flex gap-1">
              <Button size="sm" variant="outline" @click="zoomOut" :disabled="zoom <= minZoom">
                <ZoomOut class="h-4 w-4" />
              </Button>
              <span class="text-xs text-muted-foreground px-2 py-1 bg-muted rounded">{{ Math.round(zoom * 100) }}%</span>
              <Button size="sm" variant="outline" @click="zoomIn" :disabled="zoom >= maxZoom">
                <ZoomIn class="h-4 w-4" />
              </Button>
              <Button size="sm" variant="outline" @click="resetZoom" v-if="zoom !== minZoom">
                <RotateCcw class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent class="flex-1 overflow-auto p-2">
          <div v-if="data.url" ref="containerRef" class="w-full h-full bg-muted rounded-lg overflow-auto flex items-center justify-center">
            <div class="relative inline-block" :style="{ transform: `scale(${zoom})`, transformOrigin: 'top center', transition: 'transform 0.2s ease' }">
              <img 
                ref="imageRef"
                :src="data.url" 
                :alt="data.name"
                class="max-w-full max-h-full object-contain"
              />
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-full text-muted-foreground text-sm">
            No document preview available
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
