<script setup lang="ts">
import { columns } from '@/components/gl/components/columns'
import DataTable from '@/components/gl/components/DataTable.vue'
import type { GL } from '@/components/gl/data/schema'
import { Skeleton } from '@/components/ui/skeleton'
import { useGLTransactions } from '@/composables/useTaxApi'

const { glTransactions, loading, error, pagination, fetchGLTransactions } = useGLTransactions()

// Fetch GL transactions on mount
onMounted(async () => {
  await fetchGLTransactions(undefined, 1, 10)
})

// Handle page change
const handlePageChange = async (page: number) => {
  await fetchGLTransactions(undefined, page, pagination.value.pageSize)
}

// Handle page size change
const handlePageSizeChange = async (pageSize: number) => {
  await fetchGLTransactions(undefined, 1, pageSize)
}
</script>

<template>
  <div class="w-full flex flex-col items-stretch gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-3xl font-bold tracking-tight">
          GL
        </h2>
        <p class="text-muted-foreground mt-1">
          Uploaded GL transactions for review and processing
        </p>
      </div>
      <div class="flex items-center gap-2">
        <Button variant="outline" @click="navigateTo('/gl/upload')">
          Upload GL
        </Button>
        <Button variant="outline" @click="navigateTo('/gl/upload-invoice')">
          Upload Tax Invoices or Invoices
        </Button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-destructive/10 border border-destructive text-destructive px-4 py-3 rounded-lg">
      <p class="font-medium">Error loading GL transactions</p>
      <p class="text-sm mt-1">{{ error }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-4">
      <div class="rounded-md border p-4">
        <div class="flex items-center justify-between mb-4">
          <Skeleton class="h-8 w-[250px]" />
          <Skeleton class="h-8 w-[100px]" />
        </div>
        <div class="space-y-4">
          <div v-for="i in 5" :key="i" class="flex items-center space-x-4">
            <Skeleton class="h-12 w-full" />
          </div>
        </div>
      </div>
    </div>

    <!-- GL Table -->
    <div v-else>
      <DataTable :data="glTransactions" :columns="columns" :showPagination="false" />
      
      <!-- Pagination Info and Controls -->
      <div class="flex items-center justify-between px-2 py-4">
        <div class="text-sm text-muted-foreground">
          Showing {{ ((pagination.page - 1) * pagination.pageSize) + 1 }} to {{ Math.min(pagination.page * pagination.pageSize, pagination.total) }} of {{ pagination.total }} results
        </div>
        
        <div class="flex items-center space-x-6 lg:space-x-8">
          <div class="flex items-center space-x-2">
            <p class="text-sm font-medium">Rows per page</p>
            <select 
              :value="pagination.pageSize" 
              @change="(e) => handlePageSizeChange(Number((e.target as HTMLSelectElement).value))"
              class="h-8 w-[70px] rounded-md border border-input bg-background px-3 py-1 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="30">30</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
          
          <div class="flex items-center space-x-2">
            <div class="text-sm font-medium">
              Page {{ pagination.page }} of {{ pagination.totalPages }}
            </div>
          </div>
          
          <div class="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              :disabled="pagination.page === 1 || loading"
              @click="handlePageChange(pagination.page - 1)"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              :disabled="pagination.page === pagination.totalPages || loading"
              @click="handlePageChange(pagination.page + 1)"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>