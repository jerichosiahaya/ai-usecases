<script setup lang="ts">
import type { FraudCase } from '~/types'

const router = useRouter()

const { data: allCases } = await useFetch<FraudCase[]>('/api/cases', { default: () => [] })

// Calculate pending analysis cases
const pendingAnalysisCases = computed(() => {
  return allCases.value.filter(c => c.status === 'pending')
})

// Get recent cases (last 5)
const recentCases = computed(() => {
  return allCases.value.slice(0, 5)
})

// Case status colors
const statusColor = (status: string) => {
  const colorMap: Record<string, string> = {
    pending: 'warning',
    analyzing: 'info',
    completed: 'success',
    archived: 'neutral'
  }
  return colorMap[status] || 'neutral'
}

const goToNewCase = () => {
  router.push('/cases')
}

const goToChat = () => {
  router.push('/chat')
}

const goToCaseDetail = (caseId: string) => {
  router.push(`/cases/${caseId}`)
}
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="Dashboard" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>


      </UDashboardNavbar>
    </template>

    <template #body>
      <!-- Stats Row -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <!-- Total Cases Card -->
        <UPageCard variant="soft">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted font-medium">Total Cases</p>
              <p class="text-3xl font-bold mt-2">{{ allCases.length }}</p>
            </div>
            <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-info/10">
              <UIcon name="i-lucide-folder-open" class="w-6 h-6 text-info" />
            </div>
          </div>
        </UPageCard>

        <!-- Pending Analysis Card -->
        <UPageCard variant="soft">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted font-medium">Pending Analysis</p>
              <p class="text-3xl font-bold mt-2">{{ pendingAnalysisCases.length }}</p>
            </div>
            <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-primary/10">
              <UIcon name="i-lucide-archive" class="w-6 h-6 text-primary" />
            </div>
          </div>
        </UPageCard>

        <!-- Completed Analysis Card -->
        <UPageCard variant="soft">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted font-medium">Completed Analysis</p>
              <p class="text-3xl font-bold mt-2">{{ allCases.filter(c => c.status === 'completed').length }}</p>
            </div>
            <div class="flex items-center justify-center w-12 h-12 rounded-lg bg-success/10">
              <UIcon name="i-lucide-check-circle-2" class="w-6 h-6 text-success" />
            </div>
          </div>
        </UPageCard>
      </div>

      <!-- Quick Actions -->
      <div class="mb-6">
        <div class="flex gap-3">
          <UButton
            label="Create New Case"
            icon="i-lucide-plus"
            color="primary"
            size="lg"
            @click="goToNewCase"
          />
          <UButton
            label="Chat Assistant"
            icon="i-lucide-message-circle"
            color="secondary"
            variant="outline"
            size="lg"
            @click="goToChat"
          />
        </div>
      </div>

      <!-- Recent Cases Section -->
      <UPageCard variant="soft" title="Recent Cases">
        <div v-if="recentCases.length > 0" class="space-y-3">
          <div v-for="fraudCase in recentCases" :key="fraudCase.id" class="flex items-center justify-between p-4 rounded-lg hover:bg-elevated/50 transition-colors cursor-pointer" @click="goToCaseDetail(fraudCase.id)">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-1">
                <h4 class="font-medium">{{ fraudCase.name }}</h4>
                <UBadge :label="fraudCase.status" :color="statusColor(fraudCase.status) as any" variant="subtle" size="xs" class="capitalize" />
              </div>
              <p class="text-sm text-muted">{{ fraudCase.description }}</p>
            </div>
            <div class="flex items-center gap-3 shrink-0 ml-4">
              <span class="text-xs text-dimmed">{{ new Date(fraudCase.created_at).toLocaleDateString() }}</span>
              <UIcon name="i-lucide-arrow-right" class="w-4 h-4 text-muted" />
            </div>
          </div>
        </div>
        <div v-else class="text-center py-8">
          <UIcon name="i-lucide-inbox" class="w-12 h-12 text-muted mx-auto mb-2" />
          <p class="text-sm text-muted">No cases yet</p>
        </div>
      </UPageCard>
    </template>
  </UDashboardPanel>
</template>
