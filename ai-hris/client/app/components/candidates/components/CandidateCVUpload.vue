<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { UploadIcon, CheckCircleIcon, AlertCircleIcon, FileIcon } from 'lucide-vue-next'
import { toast } from 'vue-sonner'

interface UploadedFile {
  name: string
  size: number
  type: string
  uploadedAt: string
}

const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)
const uploadedFiles = ref<UploadedFile[]>([])
const dragActive = ref(false)
const uploadProgress = ref(0)

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  dragActive.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  dragActive.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  dragActive.value = false

  const files = e.dataTransfer?.files
  if (files) {
    handleFiles(files)
  }
}

const handleFileInput = (e: Event) => {
  const files = (e.target as HTMLInputElement).files
  if (files) {
    handleFiles(files)
  }
}

const handleFiles = (files: FileList) => {
  Array.from(files).forEach((file) => {
    // Validate file type
    if (!['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type)) {
      toast.error(`Invalid file type: ${file.name}. Only PDF and Word documents are allowed.`)
      return
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error(`File too large: ${file.name}. Maximum size is 10MB.`)
      return
    }

    uploadFile(file)
  })
}

const uploadFile = (file: File) => {
  isUploading.value = true

  // Simulate file upload
  const simulateUpload = setInterval(() => {
    uploadProgress.value += Math.random() * 30
    if (uploadProgress.value >= 100) {
      uploadProgress.value = 100
      clearInterval(simulateUpload)

      uploadedFiles.value.push({
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toLocaleString(),
      })

      isUploading.value = false
      uploadProgress.value = 0

      toast.success(`File uploaded successfully: ${file.name}`)
    }
  }, 300)
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
  toast.success('File removed')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0)
    return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Upload CV</CardTitle>
      <CardDescription>Upload candidate CVs in PDF or Word format (max 10MB)</CardDescription>
    </CardHeader>
    <CardContent class="space-y-6">
      <!-- Upload Area -->
      <div
        :class="[
          'relative rounded-lg border-2 border-dashed transition-colors p-8 cursor-pointer',
          dragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-muted-foreground/50',
          isUploading && 'opacity-50 cursor-not-allowed',
        ]"
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="triggerFileInput"
      >
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".pdf,.doc,.docx"
          class="hidden"
          :disabled="isUploading"
          @change="handleFileInput"
        />

        <div class="flex flex-col items-center justify-center text-center">
          <UploadIcon class="h-12 w-12 text-muted-foreground mb-3" />
          <h3 class="text-lg font-semibold mb-1">Drag and drop your files here</h3>
          <p class="text-sm text-muted-foreground mb-4">or click to select files from your computer</p>
          <Button :disabled="isUploading" type="button">
            <span v-if="!isUploading">Select Files</span>
            <span v-else>Uploading...</span>
          </Button>
        </div>

        <!-- Upload Progress -->
        <div v-if="isUploading" class="absolute inset-0 flex flex-col items-center justify-center bg-background/50 rounded-lg">
          <div class="w-24 h-1 bg-muted rounded-full overflow-hidden mb-2">
            <div class="h-full bg-primary transition-all" :style="{ width: `${uploadProgress}%` }" />
          </div>
          <p class="text-sm font-medium">{{ uploadProgress }}%</p>
        </div>
      </div>

      <!-- Uploaded Files List -->
      <div v-if="uploadedFiles.length > 0" class="space-y-3">
        <h4 class="font-semibold text-sm">Uploaded Files</h4>
        <div class="space-y-2">
          <div
            v-for="(file, index) in uploadedFiles"
            :key="index"
            class="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
          >
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <FileIcon class="h-5 w-5 text-muted-foreground shrink-0" />
              <div class="min-w-0">
                <p class="text-sm font-medium truncate">{{ file.name }}</p>
                <p class="text-xs text-muted-foreground">{{ formatFileSize(file.size) }} • {{ file.uploadedAt }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <CheckCircleIcon class="h-5 w-5 text-green-500" />
              <Button
                variant="ghost"
                size="sm"
                @click="removeFile(index)"
              >
                Remove
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Alert -->
      <Alert>
        <AlertCircleIcon class="h-4 w-4" />
        <AlertDescription>
          Supported formats: PDF (.pdf), Word (.doc, .docx). Maximum file size: 10MB per file.
        </AlertDescription>
      </Alert>
    </CardContent>
  </Card>
</template>
