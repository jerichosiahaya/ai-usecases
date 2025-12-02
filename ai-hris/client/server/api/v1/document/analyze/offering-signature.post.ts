export default defineEventHandler(async (event) => {
  const formData = await readFormData(event)
  
  // Forward the request to the backend API
  const response = await $fetch.raw('https://ai-hris-server.azurewebsites.net/api/v1/document/analyze/offering-signature', {
    method: 'POST',
    body: formData,
  })
  
  return response._data
})
