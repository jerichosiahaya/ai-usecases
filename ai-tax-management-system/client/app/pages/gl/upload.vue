<script setup lang="ts">
import { ArrowLeft, UploadCloud, Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

const router = useRouter()
const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

const goBack = () => {
  router.back()
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  const file = input.files[0]
  if (!file) return
  await uploadFile(file)
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  if (!event.dataTransfer?.files || event.dataTransfer.files.length === 0) return

  const file = event.dataTransfer.files[0]
  if (!file) return
  await uploadFile(file)
}

const uploadFile = async (file: File) => {
  isUploading.value = true
  const formData = new FormData()
  formData.append('file', file)

  try {
    const config = useRuntimeConfig()
    const { data, error } = await useFetch(`${config.public.apiBase}/api/v1/upload/file/gl`, {
      method: 'POST',
      body: formData,
    })

    if (error.value) {
      throw new Error(error.value.message)
    }

    toast.success('File uploaded successfully', {
      description: 'Redirecting to GL page...',
    })
    setTimeout(() => {
      router.push('/gl')
    }, 2000)
  }
  catch (err: any) {
    toast.error(`Upload failed: ${err.message}`)
  }
  finally {
    isUploading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="goBack">
        <ArrowLeft class="h-4 w-4" />
      </Button>
      <div>
        <h2 class="text-3xl font-bold tracking-tight">
          Upload GL
        </h2>
        <p class="text-muted-foreground mt-1">
          Upload your General Ledger file for processing
        </p>
      </div>
    </div>

    <!-- Upload Area -->
    <div
      class="border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center text-center transition-colors hover:bg-muted/50 cursor-pointer"
      :class="{ 'opacity-50 pointer-events-none': isUploading }"
      @click="triggerFileInput"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".xlsx,.csv,.json"
        class="hidden"
        @change="handleFileSelect"
      >
      <div class="p-4 rounded-full bg-muted mb-4">
        <Loader2 v-if="isUploading" class="h-8 w-8 animate-spin text-muted-foreground" />
        <UploadCloud v-else class="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-semibold">
        {{ isUploading ? 'Uploading...' : 'Click to upload or drag and drop' }}
      </h3>
      <p class="text-sm text-muted-foreground mt-1">
        XLSX, CSV or JSON (MAX. 10MB)
      </p>
      <Button class="mt-4" :disabled="isUploading">
        {{ isUploading ? 'Uploading...' : 'Select File' }}
      </Button>
    </div>
  </div>
</template>
