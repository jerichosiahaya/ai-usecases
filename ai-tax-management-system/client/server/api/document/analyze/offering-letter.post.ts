export default defineEventHandler(async (event) => {
  const formData = await readFormData(event)

  // Forward the request to the backend API
  const response = await $fetch.raw('https://ai-tax-svc.azurewebsites.net/api/v1/document/analyze/offering-letter', {
    method: 'POST',
    body: formData,
  })

  return response._data
})
