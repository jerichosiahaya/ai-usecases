<script setup lang="ts">
import { ArrowLeft, UploadCloud, Loader2, RefreshCw } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
import { Skeleton } from '@/components/ui/skeleton'

const router = useRouter()
const fileInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

interface UploadedFile {
  id: string
  originalFilename: string
  created_at: string
  status: string
  urn?: string
}

const page = ref(1)
const pageSize = ref(5)

const config = useRuntimeConfig()
const { data, status, error, refresh } = await useFetch(`${config.public.apiBase}/api/v1/upload/list`, {
  query: computed(() => ({
    page: page.value,
    page_size: pageSize.value,
  })),
})

const uploadedFiles = computed<UploadedFile[]>(() => {
  const responseData = data.value as any
  return responseData?.data?.items || []
})

const total = computed(() => {
  const responseData = data.value as any
  return responseData?.data?.total || 0
})

const goBack = () => {
  router.back()
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  // TODO: Handle multiple upload from server side so user wont have to wait for each file upload sequentially
  const files = Array.from(input.files)
  await uploadFiles(files)
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  if (!event.dataTransfer?.files || event.dataTransfer.files.length === 0) return

  const files = Array.from(event.dataTransfer.files)
  await uploadFiles(files)
}

const uploadFiles = async (files: File[]) => {
  if (files.length === 0) return

  isUploading.value = true
  let successCount = 0
  let failCount = 0

  try {
    // Upload all files in parallel
    const uploadPromises = files.map(async (file) => {
      const formData = new FormData()
      formData.append('file', file)

      try {
        const config = useRuntimeConfig()
        const { data, error } = await useFetch(`${config.public.apiBase}/api/v1/upload/file`, {
          method: 'POST',
          body: formData,
        })

        if (error.value) {
          throw new Error(error.value.message)
        }

        successCount++
      }
      catch (err: any) {
        failCount++
        console.error(`Failed to upload ${file.name}:`, err)
      }
    })

    await Promise.all(uploadPromises)

    // Show summary toast
    if (successCount > 0 && failCount === 0) {
      toast.success(`${successCount} file${successCount > 1 ? 's' : ''} uploaded successfully`)
    } else if (successCount > 0 && failCount > 0) {
      toast.warning(`${successCount} succeeded, ${failCount} failed`)
    } else if (failCount > 0) {
      toast.error(`Failed to upload ${failCount} file${failCount > 1 ? 's' : ''}`)
    }

    await refresh()
  }
  finally {
    isUploading.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div class="flex items-center gap-4">
      <Button variant="ghost" size="icon" @click="goBack">
        <ArrowLeft class="h-4 w-4" />
      </Button>
      <div>
        <h2 class="text-xl font-bold tracking-tight">
          Upload Tax Invoices/Invoices
        </h2>
        <p class="text-muted-foreground mt-1">
          Upload your Tax Invoices or Invoices for processing
        </p>
      </div>
    </div>

    <!-- Upload Area -->
    <div
      class="border-2 border-dashed rounded-lg p-12 flex flex-col items-center justify-center text-center transition-colors hover:bg-muted/50 cursor-pointer"
      :class="{ 'opacity-50 pointer-events-none': isUploading }"
      @click="triggerFileInput"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf"
        multiple
        class="hidden"
        @change="handleFileSelect"
      >
      <div class="p-4 rounded-full bg-muted mb-4">
        <Loader2 v-if="isUploading" class="h-8 w-8 animate-spin text-muted-foreground" />
        <UploadCloud v-else class="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 class="text-lg font-semibold">
        {{ isUploading ? 'Uploading...' : 'Click to upload or drag and drop' }}
      </h3>
      <p class="text-sm text-muted-foreground mt-1">
        PDF files (MAX. 10MB each) • Multiple files supported
      </p>
      <Button class="mt-4" :disabled="isUploading">
        {{ isUploading ? 'Uploading...' : 'Select File' }}
      </Button>
    </div>

    <!-- Uploaded Files List -->
    <div class="mt-8 space-y-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-xl font-semibold">
            Uploaded Documents
          </h3>
          <p class="text-sm text-muted-foreground">
            Refresh the list to see the latest status updates.
          </p>
        </div>
        <Button variant="outline" size="sm" :disabled="status === 'pending'" @click="refresh">
          <RefreshCw class="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
      <div class="border rounded-md">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Filename</TableHead>
              <TableHead>Uploaded At</TableHead>
              <TableHead>Completed At</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>URN</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <template v-if="status === 'pending'">
              <TableRow v-for="i in 5" :key="i">
                <TableCell><Skeleton class="h-4 w-[250px]" /></TableCell>
                <TableCell><Skeleton class="h-4 w-[150px]" /></TableCell>
                <TableCell><Skeleton class="h-4 w-[150px]" /></TableCell>
                <TableCell><Skeleton class="h-4 w-[100px]" /></TableCell>
                <TableCell><Skeleton class="h-4 w-[100px]" /></TableCell>
              </TableRow>
            </template>
            <template v-else>
              <TableRow v-for="file in uploadedFiles" :key="file.id">
                <TableCell>{{ file.originalFilename }}</TableCell>
                <TableCell>
                  {{ file.created_at ? new Date(file.created_at.endsWith('Z') ? file.created_at : file.created_at + 'Z').toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZone: 'Asia/Jakarta'
                  }) : '-' }}
                </TableCell>
                <TableCell>
                  {{ file.completed_at ? new Date(file.completed_at.endsWith('Z') ? file.completed_at : file.completed_at + 'Z').toLocaleString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZone: 'Asia/Jakarta'
                  }) : '-' }}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    :class="{
                      'bg-yellow-100 text-yellow-800 border-yellow-200': file.status === 'processing',
                      'bg-green-100 text-green-800 border-green-200': file.status === 'done',
                      'bg-gray-100 text-gray-800 border-gray-200': !['processing', 'done'].includes(file.status),
                    }"
                  >
                    <Loader2 v-if="file.status === 'processing'" class="mr-1 h-3 w-3 animate-spin" />
                    {{ file.status || 'Uploaded' }}
                  </Badge>
                </TableCell>
                <TableCell>
                  <NuxtLink 
                    v-if="file.urn" 
                    :to="`/gl/${file.urn}`"
                    class="font-mono text-sm text-blue-600 hover:underline"
                  >
                    {{ file.urn }}
                  </NuxtLink>
                  <span v-else class="text-muted-foreground">-</span>
                </TableCell>
              </TableRow>
              <TableRow v-if="uploadedFiles.length === 0">
                <TableCell colspan="5" class="text-center text-muted-foreground h-24">
                  No documents uploaded yet.
                </TableCell>
              </TableRow>
            </template>
          </TableBody>
        </Table>
      </div>

      <div class="mt-4 flex justify-end">
        <Pagination v-if="total > 0" v-model:page="page" :total="total" :items-per-page="pageSize" :sibling-count="1" show-edges>
          <PaginationContent v-slot="{ items }">
            <li class="flex items-center list-none">
              <PaginationPrevious />
            </li>

            <template v-for="(item, index) in items">
              <PaginationItem v-if="item.type === 'page'" :key="index" :value="item.value" :is-active="item.value === page">
                {{ item.value }}
              </PaginationItem>
              <PaginationEllipsis v-else :key="item.type" :index="index" />
            </template>

            <li class="flex items-center list-none">
              <PaginationNext />
            </li>
          </PaginationContent>
        </Pagination>
      </div>
    </div>
  </div>
</template>
