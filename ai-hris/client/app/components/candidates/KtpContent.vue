<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-vue-next'
import type { LegalDocument, KtpStructured } from './data/schema'

const props = defineProps<{
  data: LegalDocument
}>()

const imageRef = ref<HTMLImageElement | null>(null)
const zoom = ref(1)
const minZoom = 1
const maxZoom = 3

const ktpData = computed<KtpStructured>(() => {
  const content = props.data.extracted_content || {}
  return ((content as any).structured_data || content) as KtpStructured
})

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

console.log(ktpData.value)
</script>

<template>
  <div class="flex gap-6 flex-1 overflow-hidden h-full">
    <!-- Left Column: Data -->
    <div class="flex flex-col gap-6 flex-1 overflow-auto">
      <div class="space-y-6">
        <!-- Header Info -->
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-semibold">Kartu Tanda Penduduk (KTP)</h3>
            <p class="text-sm text-muted-foreground">NIK: {{ ktpData.nik || '-' }}</p>
          </div>
        </div>

        <Separator />

        <!-- Personal Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Nama Lengkap</Label>
            <p class="font-medium">{{ ktpData.name || '-' }}</p>
          </div>
          
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Tempat/Tgl Lahir</Label>
            <p class="font-medium">
              {{ ktpData.birth_place || '-' }}, {{ formatDate(ktpData.birth_date) }}
            </p>
          </div>

          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Jenis Kelamin</Label>
            <p class="font-medium">{{ ktpData.gender || '-' }}</p>
          </div>

          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Agama</Label>
            <p class="font-medium">{{ ktpData.religion || '-' }}</p>
          </div>

          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Status Perkawinan</Label>
            <p class="font-medium">{{ ktpData.marital_status || '-' }}</p>
          </div>

          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Pekerjaan</Label>
            <p class="font-medium">{{ ktpData.occupation || '-' }}</p>
          </div>

          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">Kewarganegaraan</Label>
            <p class="font-medium">{{ ktpData.nationality || '-' }}</p>
          </div>
        </div>

        <Separator />

        <!-- Address Information -->
        <div>
          <h4 class="text-sm font-semibold mb-4">Alamat</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="col-span-2 space-y-1">
              <Label class="text-xs text-muted-foreground">Alamat Lengkap</Label>
              <p class="font-medium">{{ ktpData.address || '-' }}</p>
            </div>

            <div class="space-y-1">
              <Label class="text-xs text-muted-foreground">RT/RW</Label>
              <p class="font-medium">{{ ktpData.rt_rw || '-' }}</p>
            </div>

            <div class="space-y-1">
              <Label class="text-xs text-muted-foreground">Kel/Desa</Label>
              <p class="font-medium">{{ ktpData.village || '-' }}</p>
            </div>

            <div class="space-y-1">
              <Label class="text-xs text-muted-foreground">Kecamatan</Label>
              <p class="font-medium">{{ ktpData.district || '-' }}</p>
            </div>

            <div class="space-y-1">
              <Label class="text-xs text-muted-foreground">Kota/Kabupaten</Label>
              <p class="font-medium">{{ ktpData.city || '-' }}</p>
            </div>

            <div class="space-y-1">
              <Label class="text-xs text-muted-foreground">Provinsi</Label>
              <p class="font-medium">{{ ktpData.province || '-' }}</p>
            </div>
          </div>
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
          <div v-if="data.url" class="w-full h-full bg-muted rounded-lg overflow-auto flex items-center justify-center">
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
