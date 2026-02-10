<script setup lang="ts">
import NumberFlow from '@number-flow/vue'
import { TrendingDown, TrendingUp, Users, Briefcase, UserCheck, Percent, FileText, Receipt, Database } from 'lucide-vue-next'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const { stats, loading, fetchStats } = useDashboardStats()

onMounted(async () => {
  await fetchStats()
})

const dataCard = computed(() => ({
  totalGL: stats.value.total_gl_transactions,
  totalTaxInvoices: stats.value.total_tax_invoices,
  totalInvoices: stats.value.total_invoices,
}))

const timeRange = ref('30d')

const isDesktop = useMediaQuery('(min-width: 768px)')
watch(isDesktop, () => {
  if (isDesktop.value) {
    timeRange.value = '30d'
  }
  else {
    timeRange.value = '7d'
  }
}, { immediate: true })
</script>

<template>
  <div class="w-full flex flex-col gap-4">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h2 class="text-2xl font-bold tracking-tight">
        Dashboard
      </h2>
      <div class="flex items-center space-x-2">
        <BaseDateRangePicker />
        <Button>Download</Button>
      </div>
    </div>
    <main class="@container/main flex flex-1 flex-col gap-4 md:gap-8">
      <div class="grid grid-cols-1 gap-4 *:data-[slot=card]:bg-linear-to-t *:data-[slot=card]:shadow-xs @xl/main:grid-cols-2 @5xl/main:grid-cols-3">
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Total GL Transactions</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.totalGL"
              />
            </CardTitle>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Recorded Transactions <Database class="size-4" />
            </div>
            <div class="text-muted-foreground">
              Total GL entries in system
            </div>
          </CardFooter>
        </Card>
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Total Tax Invoices</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.totalTaxInvoices"
              />
            </CardTitle>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Processed Tax Invoices <Receipt class="size-4" />
            </div>
            <div class="text-muted-foreground">
              Total tax invoices uploaded
            </div>
          </CardFooter>
        </Card>
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Total Invoices</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.totalInvoices"
              />
            </CardTitle>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Processed Invoices <FileText class="size-4" />
            </div>
            <div class="text-muted-foreground">
              Total regular invoices uploaded
            </div>
          </CardFooter>
        </Card>
      </div>
    </main>
  </div>
</template>
