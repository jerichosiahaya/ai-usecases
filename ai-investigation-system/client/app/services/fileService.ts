const API_BASE_URL = 'https://ai-investigation-server.azurewebsites.net/api/v1'

interface FileInfo {
  blob_name: string
  original_filename: string
  case_id: string
  size: number
  content_type: string
  uploaded_at: string
  url: string
}

interface ApiResponse<T> {
  status: string
  message: string
  data: T
}

export const fileService = {
  async uploadFile(caseId: string, file: File): Promise<FileInfo> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await $fetch<ApiResponse<FileInfo>>(
        `${API_BASE_URL}/upload/file/${caseId}`,
        {
          method: 'POST',
          body: formData
        }
      )
      return response.data
    } catch (error) {
      console.error('Error uploading file:', error)
      throw error
    }
  },

  async listFiles(caseId: string): Promise<FileInfo[]> {
    try {
      const response = await $fetch<ApiResponse<FileInfo[]>>(
        `${API_BASE_URL}/upload/files/${caseId}`,
        {
          method: 'GET'
        }
      )
      return response.data || []
    } catch (error) {
      console.error(`Error listing files for case ${caseId}:`, error)
      return []
    }
  },

  async deleteFile(caseId: string, blobName: string): Promise<void> {
    try {
      await $fetch(
        `${API_BASE_URL}/upload/file/${caseId}/${encodeURIComponent(blobName)}`,
        {
          method: 'DELETE'
        }
      )
    } catch (error) {
      console.error(`Error deleting file ${blobName}:`, error)
      throw error
    }
  }
}
