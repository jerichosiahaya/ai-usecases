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
    <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Document Details</DialogTitle>
        <DialogDescription>
          Extracted information from KTP document.
        </DialogDescription>
      </DialogHeader>
      
      <div class="py-4">
        <KtpContent :data="data" />
      </div>
    </DialogContent>
  </Dialog>
</template>
