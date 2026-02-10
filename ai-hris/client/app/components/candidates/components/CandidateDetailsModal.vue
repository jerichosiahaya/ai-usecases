<script setup lang="ts">
import { ref } from 'vue'
import type { Candidate } from '../data/schema'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { statuses, positions } from '../data/data'
import { StarIcon, FileTextIcon, MailIcon, PhoneIcon, BriefcaseIcon, ClockIcon, DownloadIcon } from 'lucide-vue-next'

interface CandidateDetailsModalProps {
  open: boolean
  candidate: Candidate
}

const props = defineProps<CandidateDetailsModalProps>()
const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const notes = ref(props.candidate.notes || '')

const getStatusBadgeVariant = (status: string) => {
  const statusConfig = {
    applied: 'secondary',
    reviewing: 'outline',
    shortlisted: 'default',
    rejected: 'destructive',
    hired: 'default',
  }
  return statusConfig[status as keyof typeof statusConfig] || 'secondary'
}

const statusLabel = computed(() => {
  return statuses.find(s => s.value === props.candidate.status)?.label || props.candidate.status
})

const positionLabel = computed(() => {
  return positions.find(p => p.value === props.candidate.position)?.label || props.candidate.position
})
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-2xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <div class="flex items-start justify-between gap-4 pr-6">
          <div>
            <DialogTitle class="text-2xl">{{ candidate.name }}</DialogTitle>
            <DialogDescription>{{ positionLabel }}</DialogDescription>
          </div>
          <Badge :variant="getStatusBadgeVariant(candidate.status) as any" class="shrink-0">
            {{ statusLabel }}
          </Badge>
        </div>
      </DialogHeader>

      <div class="space-y-6">
        <!-- Contact Information -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">Contact Information</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div class="flex items-center gap-3">
              <MailIcon class="h-4 w-4 text-muted-foreground" />
              <div class="flex-1">
                <p class="text-sm text-muted-foreground">Email</p>
                <p class="text-sm font-medium">{{ candidate.email }}</p>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <PhoneIcon class="h-4 w-4 text-muted-foreground" />
              <div class="flex-1">
                <p class="text-sm text-muted-foreground">Phone</p>
                <p class="text-sm font-medium">{{ candidate.phone }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Professional Information -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">Professional Information</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <BriefcaseIcon class="h-4 w-4 text-muted-foreground" />
                  <p class="text-sm text-muted-foreground">Position</p>
                </div>
                <p class="text-sm font-medium">{{ positionLabel }}</p>
              </div>
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <ClockIcon class="h-4 w-4 text-muted-foreground" />
                  <p class="text-sm text-muted-foreground">Experience</p>
                </div>
                <p class="text-sm font-medium">{{ candidate.experience }} years</p>
              </div>
            </div>

            <Separator />

            <!-- Skills -->
            <div>
              <p class="text-sm font-medium mb-2">Skills</p>
              <div class="flex flex-wrap gap-2">
                <Badge v-for="skill in candidate.skills" :key="skill" variant="secondary">
                  {{ skill }}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Rating and Dates -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">Assessment</CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <StarIcon class="h-4 w-4 text-yellow-500" />
                  <p class="text-sm text-muted-foreground">Rating</p>
                </div>
                <p class="text-lg font-medium">{{ candidate.rating?.toFixed(1) || 'N/A' }} / 5.0</p>
              </div>
              <div>
                <p class="text-sm text-muted-foreground mb-1">Applied Date</p>
                <p class="text-sm font-medium">{{ new Date(candidate.appliedDate).toLocaleDateString() }}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Notes -->
        <Card>
          <CardHeader>
            <CardTitle class="text-lg">Notes</CardTitle>
            <CardDescription>Internal notes about the candidate</CardDescription>
          </CardHeader>
          <CardContent>
            <Textarea v-model="notes" placeholder="Add internal notes..." class="min-h-24" @blur="() => {
              // Save notes logic here
            }" />
          </CardContent>
        </Card>

        <!-- CV Document -->
        <Card v-if="candidate.cv_url">
          <CardHeader>
            <CardTitle class="text-lg">CV Document</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline" class="w-full gap-2">
              <DownloadIcon class="h-4 w-4" />
              Download CV
            </Button>
          </CardContent>
        </Card>
      </div>
    </DialogContent>
  </Dialog>
</template>
