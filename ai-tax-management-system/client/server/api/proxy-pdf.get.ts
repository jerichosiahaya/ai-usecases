export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const url = query.url as string

  if (!url) {
    throw createError({
      statusCode: 400,
      message: 'Missing url parameter',
    })
  }

  // Validate that the URL is from your allowed blob storage
  if (!url.startsWith('https://protohub.blob.core.windows.net/')) {
    throw createError({
      statusCode: 403,
      message: 'URL not allowed',
    })
  }

  try {
    const response = await fetch(url)

    if (!response.ok) {
      throw createError({
        statusCode: response.status,
        message: `Failed to fetch PDF: ${response.statusText}`,
      })
    }

    const arrayBuffer = await response.arrayBuffer()

    setHeader(event, 'Content-Type', 'application/pdf')
    setHeader(event, 'Cache-Control', 'public, max-age=3600')

    return new Uint8Array(arrayBuffer)
  }
  catch (error: any) {
    throw createError({
      statusCode: 500,
      message: error.message || 'Failed to fetch PDF',
    })
  }
})
