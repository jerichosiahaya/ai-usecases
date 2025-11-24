<script setup lang="ts">
import type { FraudCase } from '~/types'

const props = defineProps<{
  cases: FraudCase[]
  loading?: boolean
}>()

const emits = defineEmits<{
  select: [caseId: string]
}>()

const searchQuery = ref('')
const selectedStatus = ref<string | null>(null)

const filteredCases = computed(() => {
  return props.cases.filter((c) => {
    const matchesSearch = c.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = !selectedStatus.value || c.status === selectedStatus.value
    return matchesSearch && matchesStatus
  })
})

const statusBadgeColor: Record<string, 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'error' | 'neutral'> = {
  pending: 'warning',
  analyzing: 'info',
  completed: 'success',
  archived: 'neutral'
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="shrink-0 border-b border-default p-4 sm:p-6">
      <h2 class="text-lg font-semibold mb-4">Select a Case to Start Chat</h2>
      
      <div class="space-y-3">
        <UInput
          v-model="searchQuery"
          icon="i-lucide-search"
          placeholder="Search cases by name or description..."
          color="neutral"
        />
        
        <USelect
          v-model="selectedStatus"
          :options="[
            { value: null, label: 'All Statuses' },
            { value: 'pending', label: 'Pending' },
            { value: 'analyzing', label: 'Analyzing' },
            { value: 'completed', label: 'Completed' },
            { value: 'archived', label: 'Archived' }
          ]"
          option-attribute="label"
          value-attribute="value"
          placeholder="Filter by status"
        />
      </div>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="loading" class="flex items-center justify-center h-full">
        <div class="text-center">
          <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin mx-auto mb-2" />
          <p class="text-sm text-dimmed">Loading cases...</p>
        </div>
      </div>

      <div v-else-if="filteredCases.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center text-dimmed">
          <UIcon name="i-lucide-inbox" class="size-12 mx-auto mb-2" />
          <p class="text-sm">No cases found</p>
        </div>
      </div>

      <div v-else class="divide-y divide-default">
        <button
          v-for="fraudCase in filteredCases"
          :key="fraudCase.id"
          class="w-full p-4 sm:p-6 text-left transition-colors hover:bg-primary/5 border-l-2 border-transparent hover:border-primary"
          @click="emits('select', fraudCase.id)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-semibold text-highlighted truncate">
                  {{ fraudCase.name }}
                </h3>
                <UBadge
                  :label="fraudCase.status"
                  :color="statusBadgeColor[fraudCase.status]"
                  variant="subtle"
                  class="capitalize shrink-0"
                />
              </div>

              <p class="text-sm text-dimmed line-clamp-2 mb-2">
                {{ fraudCase.description }}
              </p>

              <div class="flex items-center gap-4 text-xs text-muted">
                <span>ID: {{ fraudCase.id }}</span>
                <span>Created: {{ new Date(fraudCase.createdAt).toLocaleDateString() }}</span>
              </div>
            </div>

            <UIcon name="i-lucide-chevron-right" class="size-5 shrink-0 text-muted" />
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
