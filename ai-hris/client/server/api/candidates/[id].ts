export default defineEventHandler(async (event): Promise<any> => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl || 'http://localhost:8000'
  const id = getRouterParam(event, 'id')

  if (!id) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Candidate ID is required',
    })
  }

  try {
    const response: any = await $fetch<any>(`${apiUrl}/api/v1/hr/candidate/${id}`)
    // Extract the data object from the response wrapper
    return response?.data || response
  } catch (error) {
    console.error('Error fetching candidate:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch candidate',
    })
  }
})
