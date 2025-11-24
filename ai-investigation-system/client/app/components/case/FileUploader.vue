<script setup lang="ts">
import { ref } from 'vue'
import { useFileManager } from '~/composables/useCaseApi'

const props = defineProps<{
  caseId: string
}>()

const emit = defineEmits<{
  fileUploaded: []
}>()

const { loading, uploadFile, deleteFile } = useFileManager()
const fileInput = ref<HTMLInputElement>()
const uploadingFile = ref<string | null>(null)

const handleFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  for (const file of input.files) {
    uploadingFile.value = file.name
    try {
      await uploadFile(props.caseId, file)
      // Emit event after successful upload
      emit('fileUploaded')
    } catch (error) {
      console.error(`Failed to upload ${file.name}:`, error)
    } finally {
      uploadingFile.value = null
    }
  }

  // Reset input
  input.value = ''
}

const triggerFileInput = () => {
  fileInput?.value?.click()
}
</script>

<template>
  <div class="space-y-4">
    <!-- Upload Area -->
    <div class="border-2 border-dashed border-primary/30 rounded-lg p-6 hover:border-primary/50 transition-colors">
      <div class="flex flex-col items-center justify-center text-center">
        <UIcon name="i-lucide-upload-cloud" class="w-8 h-8 text-muted mb-2" />
        <p class="text-sm font-medium text-highlighted mb-1">
          {{ uploadingFile ? `Uploading ${uploadingFile}...` : 'Upload Files' }}
        </p>
        <p class="text-xs text-muted mb-4">
          Drag and drop files here or click to browse
        </p>
        <UButton
          label="Choose Files"
          icon="i-lucide-file-up"
          color="primary"
          size="sm"
          :loading="loading || !!uploadingFile"
          @click="triggerFileInput"
        />
      </div>
      <input
        ref="fileInput"
        type="file"
        multiple
        class="hidden"
        @change="handleFileSelect"
      />
    </div>
  </div>
</template>
