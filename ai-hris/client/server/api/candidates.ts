export default defineEventHandler(async (event): Promise<any> => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl || 'https://ai-hris-server.azurewebsites.net'

  try {
    const response: any = await $fetch<any>(`${apiUrl}/api/v1/hr/candidates`)
    // Extract the data array from the response wrapper
    return response?.data || response
  } catch (error) {
    console.error('Error fetching candidates:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch candidates',
    })
  }
})
