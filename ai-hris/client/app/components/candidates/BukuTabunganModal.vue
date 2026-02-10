<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import BukuTabunganContent from './BukuTabunganContent.vue'
import type { BukuTabungan } from './data/schema'

const props = defineProps<{
  open: boolean
  data?: BukuTabungan
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
      <DialogHeader class="shrink-0">
        <DialogTitle>Buku Tabungan Details</DialogTitle>
        <DialogDescription>
          Extracted data from the uploaded Buku Tabungan document.
        </DialogDescription>
      </DialogHeader>

      <BukuTabunganContent v-if="data" :data="data" />

      <div v-else class="py-8 text-center text-muted-foreground">
        No structured data available for this document.
      </div>
    </DialogContent>
  </Dialog>
</template>
