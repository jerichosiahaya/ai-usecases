import { ref, reactive } from 'vue'
import { caseService } from '~/services/caseService'
import { fileService } from '~/services/fileService'
import type { FraudCase, CreateCasePayload } from '~/types'

export const useCreateCase = () => {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const success = ref(false)

  const formData = reactive({
    name: '',
    description: '',
    files: [] as File[]
  })

  const resetForm = () => {
    formData.name = ''
    formData.description = ''
    formData.files = []
    error.value = null
    success.value = false
  }

  const addFiles = (files: FileList | null) => {
    if (!files) return
    formData.files = [...formData.files, ...Array.from(files)]
  }

  const removeFile = (index: number) => {
    formData.files.splice(index, 1)
  }

  const submitForm = async (): Promise<FraudCase | null> => {
    loading.value = true
    error.value = null

    try {
      if (!formData.name.trim() || !formData.description.trim()) {
        throw new Error('Name and description are required')
      }

      const payload: CreateCasePayload = {
        name: formData.name,
        description: formData.description,
        files: formData.files
      }

      const createdCase = await caseService.createCase(payload)

      // Upload files if any
      if (formData.files.length > 0) {
        for (const file of formData.files) {
          try {
            await fileService.uploadFile(createdCase.id, file)
          } catch (fileError) {
            console.error(`Failed to upload file ${file.name}:`, fileError)
          }
        }
      }

      success.value = true
      resetForm()
      return createdCase
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'An error occurred'
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    success,
    formData,
    resetForm,
    addFiles,
    removeFile,
    submitForm
  }
}

export const useCaseManager = () => {
  const cases = ref<FraudCase[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchCases = async () => {
    loading.value = true
    error.value = null
    try {
      cases.value = await caseService.getCases()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load cases'
    } finally {
      loading.value = false
    }
  }

  const deleteCase = async (id: string) => {
    loading.value = true
    error.value = null
    try {
      await caseService.deleteCase(id)
      cases.value = cases.value.filter(c => c.id !== id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete case'
    } finally {
      loading.value = false
    }
  }

  const updateCaseStatus = async (id: string, status: string) => {
    loading.value = true
    error.value = null
    try {
      const updated = await caseService.updateCase(id, { status } as any)
      const index = cases.value.findIndex(c => c.id === id)
      if (index !== -1) {
        cases.value[index] = updated
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update case'
    } finally {
      loading.value = false
    }
  }

  return {
    cases,
    loading,
    error,
    fetchCases,
    deleteCase,
    updateCaseStatus
  }
}

export const useFileManager = () => {
  const files = ref<any[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const loadFiles = async (caseId: string) => {
    loading.value = true
    error.value = null
    try {
      files.value = await fileService.listFiles(caseId)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load files'
    } finally {
      loading.value = false
    }
  }

  const uploadFile = async (caseId: string, file: File) => {
    loading.value = true
    error.value = null
    try {
      const uploadedFile = await fileService.uploadFile(caseId, file)
      files.value.push(uploadedFile)
      return uploadedFile
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to upload file'
    } finally {
      loading.value = false
    }
  }

  const deleteFile = async (caseId: string, blobName: string) => {
    loading.value = true
    error.value = null
    try {
      await fileService.deleteFile(caseId, blobName)
      files.value = files.value.filter(f => f.blob_name !== blobName)
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete file'
    } finally {
      loading.value = false
    }
  }

  return {
    files,
    loading,
    error,
    loadFiles,
    uploadFile,
    deleteFile
  }
}
