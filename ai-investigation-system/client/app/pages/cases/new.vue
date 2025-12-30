<script setup lang="ts">
import { caseService } from '~/services/caseService'

const router = useRouter()
const toast = useToast()

const form = reactive({
  name: '',
  description: ''
})

const isLoading = ref(false)
const caseIdForUpload = ref<string | null>(null)

const ALLOWED_FILE_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'image/jpeg', 'image/png', 'image/svg+xml']
const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.jpg', '.png', '.svg', '.jpeg']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10 MB

// Track uploaded files with their status
const uploadedFiles = reactive<{
  [key: string]: { file: File; status: 'pending' | 'uploading' | 'completed' | 'error'; error?: string }
}>({})

const validateFile = (file: File): { valid: boolean; error?: string } => {
  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `File "${file.name}" exceeds 10 MB limit (${(file.size / 1024 / 1024).toFixed(2)} MB)`
    }
  }

  // Check file type by MIME type and extension
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
  const isValidMime = ALLOWED_FILE_TYPES.includes(file.type)
  const isValidExtension = ALLOWED_EXTENSIONS.includes(fileExtension)

  if (!isValidMime && !isValidExtension) {
    return {
      valid: false,
      error: `File "${file.name}" has unsupported format. Allowed: PDF, DOCX, TXT, JPG, PNG, SVG, JPEG`
    }
  }

  return { valid: true }
}

// Auto-upload files BEFORE case creation to get URLs
const uploadFilesFirst = async (): Promise<string[]> => {
  const fileKeys = Object.keys(uploadedFiles).filter(k => {
    const entry = uploadedFiles[k]
    return entry && entry.status === 'pending'
  })

  const uploadedUrls: string[] = []

  // Create a temporary case ID for file upload organization
  const tempCaseId = 'temp-' + Date.now()

  for (const fileKey of fileKeys) {
    const fileEntry = uploadedFiles[fileKey]
    if (!fileEntry) continue

    fileEntry.status = 'uploading'

    try {
      const formData = new FormData()
      formData.append('file', fileEntry.file)

      const response = await $fetch<{ status: string; message: string; data?: any }>(`https://ai-hris-server.azurewebsites.net/api/v1/upload/file/${tempCaseId}`, {
        method: 'POST',
        body: formData
      })

      console.log('Upload response:', response)

      if (response?.status === 'Success' || response?.status === 'success') {
        fileEntry.status = 'completed'
        // Collect the URL from the response
        if (response.data?.url) {
          uploadedUrls.push(response.data.url)
          console.log('File URL collected:', response.data.url)
        } else {
          console.warn('No URL in response data:', response.data)
        }
        toast.add({
          title: 'File Uploaded',
          description: `${fileEntry.file.name} uploaded successfully`,
          color: 'success'
        })
      }
    } catch (error: any) {
      fileEntry.status = 'error'
      fileEntry.error = error?.data?.message || 'Upload failed'
      console.error('Upload error:', error)
      toast.add({
        title: 'Upload Error',
        description: `${fileEntry.file.name}: ${fileEntry.error}`,
        color: 'error'
      })
    }
  }

  console.log('All uploaded URLs:', uploadedUrls)
  return uploadedUrls
}

const handleFileSelect = (newFiles: File[]) => {
  const validFiles: File[] = []
  const errors: string[] = []

  newFiles.forEach(file => {
    const validation = validateFile(file)
    if (validation.valid) {
      validFiles.push(file)
    } else if (validation.error) {
      errors.push(validation.error)
    }
  })

  if (errors.length > 0) {
    toast.add({
      title: 'File Validation Error',
      description: errors.join('\n'),
      color: 'error'
    })
  }

  if (validFiles.length > 0) {
    // Add files to upload queue
    validFiles.forEach(file => {
      const uniqueKey = `${file.name}-${Date.now()}-${Math.random()}`
      uploadedFiles[uniqueKey] = {
        file,
        status: 'pending'
      }
    })

    toast.add({
      title: 'Files Added',
      description: `${validFiles.length} file(s) ready to upload (will be uploaded after case creation)`,
      color: 'success'
    })
  }
}

const handleRemoveFile = (fileKey: string | number) => {
  delete uploadedFiles[fileKey as string]
}

const handleSubmit = async () => {
  const uploadedFileCount = Object.keys(uploadedFiles).length

  if (!form.name || !form.description || uploadedFileCount === 0) {
    toast.add({
      title: 'Validation Error',
      description: 'Please fill all fields and add at least one file',
      color: 'error'
    })
    return
  }

  isLoading.value = true
  try {
    // Step 1: Upload files FIRST to get URLs
    toast.add({
      title: 'Uploading Files',
      description: 'Uploading files to storage...',
      color: 'info'
    })
    const fileUrls = await uploadFilesFirst()

    console.log('File URLs collected:', fileUrls)

    if (fileUrls.length === 0) {
      toast.add({
        title: 'Error',
        description: 'No files were successfully uploaded',
        color: 'error'
      })
      isLoading.value = false
      return
    }

    // Step 2: Transform URLs to new schema format with url, name, description, and format
    const filesWithMetadata = fileUrls.map((url, index) => {
      const fileName = url.split('/').pop() || url
      const fileFormat = fileName.split('.').pop()?.toLowerCase() || ''

      // Get the original file name from uploadedFiles
      const originalFileName = Object.values(uploadedFiles)[index]?.file.name || fileName

      return {
        url: url,
        name: originalFileName,
        description: '',
        format: fileFormat
      }
    })

    // Step 3: Create case WITH the file URLs in new schema format
    const newCase = await caseService.createCase({
      name: form.name,
      description: form.description,
      files: filesWithMetadata
    })

    console.log('Case created with URLs:', newCase)

    toast.add({
      title: 'Success',
      description: 'Case created with files successfully',
      color: 'success'
    })

    // Navigate to case detail page
    router.push(`/cases/${newCase.id}`)
  } catch (error) {
    console.error('Error:', error)
    toast.add({
      title: 'Error',
      description: 'Failed to create case or upload files',
      color: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <UDashboardPanel id="new-case">
    <template #header>
      <UDashboardNavbar title="New Case">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="flex gap-6">
        <div class="w-full">
          <UPageCard variant="soft" title="Create New Case">
            <div class="space-y-5">
              <UFormField label="Case Name" required help="Enter a descriptive name for this case" class="w-full">
                <UInput v-model="form.name" placeholder="e.g., Tax Fraud PT XYZ" class="w-full" />
              </UFormField>

              <UFormField label="Description" required help="Provide details about the case" class="w-full">
                <UTextarea v-model="form.description"
                  placeholder="Describe the case details, suspicions, and relevant information..." class="w-full" />
              </UFormField>

              <UFormField label="Upload Files" required
                help="Upload documents, evidence, or data files related to this case">
                <div class="border-2 border-dashed border-gray-300 rounded-lg p-6">
                  <input type="file" multiple class="hidden" id="file-input"
                    accept=".pdf,.docx,.txt,.jpg,.png,.svg,.jpeg"
                    @change="(e) => handleFileSelect(Array.from((e.target as HTMLInputElement).files || []))" />
                  <label for="file-input" class="cursor-pointer flex flex-col items-center gap-2">
                    <UIcon name="i-lucide-upload" class="w-8 h-8 text-gray-400" />
                    <span class="text-sm font-medium">Click to upload or drag and drop</span>
                    <span class="text-xs text-gray-500">PDF, DOCX, TXT, JPG, PNG, SVG, JPEG (max 10 MB each)</span>
                  </label>

                  <div v-if="Object.keys(uploadedFiles).length > 0" class="mt-4 space-y-2">
                    <div v-for="(entry, fileKey) in uploadedFiles" :key="fileKey"
                      class="flex items-center justify-between bg-info p-3 rounded">
                      <div class="flex items-center gap-2 flex-1 min-w-0">
                        <UIcon
                          :name="entry.status === 'completed' ? 'i-lucide-check-circle-2' : entry.status === 'uploading' ? 'i-lucide-loader' : entry.status === 'error' ? 'i-lucide-alert-circle' : 'i-lucide-clock'"
                          :class="[
                            'w-4 h-4 shrink-0',
                            entry.status === 'completed' ? 'text-success' : entry.status === 'uploading' ? 'text-warning animate-spin' : entry.status === 'error' ? 'text-error' : 'text-gray-400'
                          ]" />
                        <span class="text-sm truncate">{{ entry.file.name }}</span>
                        <span class="text-xs shrink-0 text-white">({{ (entry.file.size / 1024 / 1024).toFixed(2) }}
                          MB)</span>
                      </div>
                      <UButton icon="i-lucide-x" color="neutral" variant="ghost" size="xs"
                        :disabled="entry.status === 'uploading'" @click="handleRemoveFile(fileKey)" />
                    </div>
                  </div>
                </div>
              </UFormField>

              <div class="flex gap-3 pt-4">
                <UButton label="Create Case" color="primary" :loading="isLoading" @click="handleSubmit" />
                <UButton label="Cancel" color="neutral" variant="outline" @click="router.push('/cases')" />
              </div>
            </div>
          </UPageCard>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>