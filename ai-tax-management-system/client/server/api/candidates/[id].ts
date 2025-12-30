export default defineEventHandler(async (event): Promise<any> => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl || 'https://ai-hris-server.azurewebsites.net'
  const id = getRouterParam(event, 'id')
  const method = event.method

  if (!id) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Candidate ID is required',
    })
  }

  try {
    const fetchOptions: any = {
      method: method
    }

    if (method !== 'GET' && method !== 'HEAD') {
      fetchOptions.body = await readBody(event)
    }

    const response: any = await $fetch<any>(`${apiUrl}/api/v1/hr/candidate/${id}`, fetchOptions)
    // Extract the data object from the response wrapper
    console.log(`Successfully ${method} candidate:`, response)
    return response?.data || response
  } catch (error) {
    console.error(`Error ${method} candidate:`, error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to process candidate request',
    })
  }
})
