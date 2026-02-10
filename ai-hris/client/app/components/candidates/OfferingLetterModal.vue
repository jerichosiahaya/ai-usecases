    <script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import OfferingLetterContent from './OfferingLetterContent.vue'
import type { OfferingLetter } from './data/schema'

const props = defineProps<{
  open: boolean
  data?: OfferingLetter
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
      <DialogHeader class="shrink-0">
        <DialogTitle>Offering Letter Details</DialogTitle>
        <DialogDescription>
          Review the signed offering letter details and extracted information.
        </DialogDescription>
      </DialogHeader>

      <OfferingLetterContent v-if="data" :data="data" />

      <div v-else class="py-8 text-center text-muted-foreground">
        No data available for this document.
      </div>
    </DialogContent>
  </Dialog>
</template>
