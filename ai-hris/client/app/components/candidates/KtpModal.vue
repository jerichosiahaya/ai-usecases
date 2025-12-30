<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import KtpContent from './KtpContent.vue'
import type { LegalDocument } from './data/schema'

defineProps<{
  open: boolean
  data: LegalDocument
}>()

defineEmits<{
  'update:open': [value: boolean]
}>()
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
      <DialogHeader class="shrink-0">
        <DialogTitle>Document Details</DialogTitle>
        <DialogDescription>
          Extracted information from KTP document.
        </DialogDescription>
      </DialogHeader>
      
      <div class="flex-1 min-h-0 py-4">
        <KtpContent :data="data" />
      </div>
    </DialogContent>
  </Dialog>
</template>
