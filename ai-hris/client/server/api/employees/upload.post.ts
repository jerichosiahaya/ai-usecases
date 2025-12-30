import { defineEventHandler, readMultipartFormData, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl || 'https://ai-hris-server.azurewebsites.net'

  const body = await readMultipartFormData(event)
  if (!body) {
    throw createError({ statusCode: 400, message: 'No multipart data found' })
  }

  const formData = new FormData()

  for (const part of body) {
    if (part.filename) {
      // Create a Blob from the buffer
      const blob = new Blob([part.data], { type: part.type })
      formData.append(part.name!, blob, part.filename)
    } else {
      formData.append(part.name!, part.data.toString())
    }
  }

  try {
    const response = await $fetch(`${apiUrl}/api/v1/hr/document/upload`, {
      method: 'POST',
      body: formData
    })
    return response
  } catch (error: any) {
    console.error('Upload error:', error)
    throw createError({
      statusCode: error.statusCode || 500,
      message: error.message || 'Upload failed'
    })
  }
})
