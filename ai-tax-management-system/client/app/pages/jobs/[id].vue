<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Job } from '@/components/jobs/data/schema'
import jobsData from '@/components/jobs/data/jobs.json'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  ArrowLeft,
  MapPin,
  Clock,
  Calendar,
  Briefcase,
  Users,
  Building2,
  DollarSign,
  MoreHorizontal,
  Edit,
  Trash2,
  CheckCircle2
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const jobs = (jobsData as { data: Job[] }).data
const jobId = route.params.id as string
const job = computed(() => jobs.find(j => j.id === jobId))

const goBack = () => {
  router.back()
}

const formatCurrency = (amount: number, currency: string) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0
  }).format(amount)
}
</script>

<template>
  <div v-if="job" class="min-h-screen bg-muted/40">
    <div class="max-w-7xl mx-auto p-6 space-y-6">
      
      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div class="flex items-start gap-4">
          <Button variant="ghost" size="icon" @click="goBack" class="mt-1">
            <ArrowLeft class="h-5 w-5" />
          </Button>
          <div>
            <div class="flex items-center gap-3 mb-1">
              <h1 class="text-2xl font-bold tracking-tight text-foreground">{{ job.title }}</h1>
              <Badge variant="outline" :class="{
                'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30': job.status === 'Open',
                'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700': job.status === 'Closed',
                'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-900/30': job.status === 'Draft'
              }">
                {{ job.status }}
              </Badge>
            </div>
            <div class="flex items-center gap-2 text-sm text-muted-foreground">
              <span>{{ job.id }}</span>
              <span>•</span>
              <span>{{ job.department }}</span>
            </div>
          </div>
        </div>
        
        <div class="flex gap-2">
          <Button variant="outline">
            <Edit class="mr-2 h-4 w-4" />
            Edit Job
          </Button>
          <Button variant="destructive" size="icon">
            <Trash2 class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Content -->
        <div class="lg:col-span-2 space-y-6">
          
          <!-- Description -->
          <Card>
            <CardHeader>
              <CardTitle>Job Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p class="text-sm text-muted-foreground leading-relaxed">
                {{ job.description || 'No description provided.' }}
              </p>
            </CardContent>
          </Card>

          <!-- Requirements -->
          <Card>
            <CardHeader>
              <CardTitle>Requirements</CardTitle>
            </CardHeader>
            <CardContent>
              <ul class="list-disc list-inside space-y-2 text-sm text-muted-foreground">
                <li v-for="(req, index) in job.requirements" :key="index">
                  {{ req }}
                </li>
                <li v-if="!job.requirements?.length">No specific requirements listed.</li>
              </ul>
            </CardContent>
          </Card>

          <!-- Benefits -->
          <Card v-if="job.benefits?.length">
            <CardHeader>
              <CardTitle>Benefits & Perks</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div v-for="(benefit, index) in job.benefits" :key="index" class="flex items-center gap-2 text-sm text-muted-foreground">
                  <!-- <CheckCircle2 class="h-4 w-4 text-green-500" />
                  <span>{{ benefit }}</span> -->
                  <span>Vendor Name     : {{ benefit }}</span>
                  <span>Reference       : {{ benefit }}</span>
                  <span>Document No     :{{ benefit }}</span>
                  <span>PO number       :{{ benefit }}</span>
                  <span>Document Date   :{{ benefit }}</span>
                  <span>WHT Review      :{{ benefit }}</span>
                  <span>Diff Normal     :{{ benefit }}</span>
                  <span>Ref             :{{ benefit }}</span>
                  <span>1st Vouching    :{{ benefit }}</span>
                  <span>2nd Reviewer    :{{ benefit }}</span>
                  <span>WHT Slip Number :{{ benefit }}</span>
                  <span>Document Type   :{{ benefit }}</span>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>

        
      </div>
    </div>
  </div>
  <div v-else class="min-h-screen flex items-center justify-center bg-muted/40">
    <div class="text-center">
      <h2 class="text-2xl font-bold text-foreground">GL Not Found</h2>
      <p class="text-muted-foreground mt-2">The GL you are looking for does not exist.</p>
      <Button class="mt-4" @click="goBack">Go Back</Button>
    </div>
  </div>
</template>
