<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import KartuKeluargaContent from './KartuKeluargaContent.vue'
import type { LegalDocument } from './data/schema'

const props = defineProps<{
  open: boolean
  data?: LegalDocument
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
      <DialogHeader class="shrink-0">
        <DialogTitle>Kartu Keluarga Details</DialogTitle>
        <DialogDescription>
          Extracted data from the uploaded Kartu Keluarga document.
        </DialogDescription>
      </DialogHeader>

      <KartuKeluargaContent v-if="data" :data="data" />

      <div v-else class="py-8 text-center text-muted-foreground">
        No structured data available for this document.
      </div>
    </DialogContent>
  </Dialog>
</template>
