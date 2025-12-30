<script setup lang="ts">
import { VuePDF, usePDF } from '@tato30/vue-pdf'
import '@tato30/vue-pdf/style.css'

const props = defineProps<{
  url: string
}>()

// Proxy the PDF through our server to avoid CORS issues
// const proxyUrl = computed(() => `/api/proxy-pdf?url=${encodeURIComponent(props.url)}`)

const { pdf, pages } = usePDF(props.url)
</script>

<template>
  <div class="h-full overflow-y-auto border rounded-lg bg-muted/20">
    <div class="flex flex-col items-center gap-4 p-4">
      <VuePDF
        v-for="page in pages"
        :key="page"
        :pdf="pdf"
        :page="page"
        class="shadow-md"
      />
    </div>
  </div>
</template>
