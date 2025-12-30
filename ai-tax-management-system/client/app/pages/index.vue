<script setup lang="ts">
import NumberFlow from '@number-flow/vue'
import { TrendingDown, TrendingUp, Users, Briefcase, UserCheck, Percent } from 'lucide-vue-next'
import jobsData from '@/components/jobs/data/jobs.json'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const dataCard = ref({
  totalApplicants: 0,
  openPositions: 0,
  activeCandidates: 0,
  placementRate: 0,
})

const openJobs = computed(() => {
  return (jobsData as any).data.filter((job: any) => job.status === 'Open').slice(0, 5)
})

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
      <div class="grid grid-cols-1 gap-4 *:data-[slot=card]:bg-linear-to-t *:data-[slot=card]:shadow-xs @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Total Applicants</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.totalApplicants"
              />
            </CardTitle>
            <CardAction>
              <Badge variant="outline">
                <TrendingUp class="h-4 w-4 mr-1" />
                +12.5%
              </Badge>
            </CardAction>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Trending up this month <Users class="size-4" />
            </div>
            <div class="text-muted-foreground">
              Across all open positions
            </div>
          </CardFooter>
        </Card>
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Open Positions</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.openPositions"
              />
            </CardTitle>
            <CardAction>
              <Badge variant="outline">
                <TrendingUp class="h-4 w-4 mr-1" />
                +2
              </Badge>
            </CardAction>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Actively hiring <Briefcase class="size-4" />
            </div>
            <div class="text-muted-foreground">
              In various departments
            </div>
          </CardFooter>
        </Card>
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Active Candidates</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.activeCandidates"
              />
            </CardTitle>
            <CardAction>
              <Badge variant="outline">
                <TrendingUp class="h-4 w-4 mr-1" />
                +5
              </Badge>
            </CardAction>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Currently in pipeline <UserCheck class="size-4" />
            </div>
            <div class="text-muted-foreground">
              Reviewing and interviewing
            </div>
          </CardFooter>
        </Card>
        <Card class="@container/card">
          <CardHeader>
            <CardDescription>Placement Rate</CardDescription>
            <CardTitle class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
              <NumberFlow
                :value="dataCard.placementRate"
                suffix="%"
              />
            </CardTitle>
            <CardAction>
              <Badge variant="outline">
                <TrendingUp class="h-4 w-4 mr-1" />
                +4.5%
              </Badge>
            </CardAction>
          </CardHeader>
          <CardFooter class="flex-col items-start gap-1.5 text-sm">
            <div class="line-clamp-1 flex gap-2 font-medium">
              Successful hires <Percent class="size-4" />
            </div>
            <div class="text-muted-foreground">
              Meeting hiring targets
            </div>
          </CardFooter>
        </Card>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Current Job Openings -->
        <Card>
          <CardHeader>
            <CardTitle>Current Job Openings</CardTitle>
            <CardDescription>Positions currently accepting applications</CardDescription>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <div v-for="job in openJobs" :key="job.id" class="flex items-center justify-between">
                <div class="space-y-1">
                  <p class="text-sm font-medium leading-none">{{ job.title }}</p>
                  <p class="text-xs text-muted-foreground">{{ job.department }} • {{ job.location }}</p>
                </div>
                <Badge variant="secondary">{{ job.type }}</Badge>
              </div>
              <div v-if="openJobs.length === 0" class="text-sm text-muted-foreground">
                No open positions at the moment.
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  </div>
</template>
