<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import type { KartuKeluargaStructured, LegalDocument } from './data/schema'

const props = defineProps<{
  open: boolean
  data?: LegalDocument
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
}>()

// Helper to format date
const formatDate = (dateString: string) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString('id-ID', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch (e) {
    return dateString
  }
}

console.log('KartuKeluargaModal data prop:', props.data)
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="w-[95vw] max-w-none! h-[95vh] flex flex-col p-6">
      <DialogHeader class="shrink-0">
        <DialogTitle>Kartu Keluarga Details</DialogTitle>
        <DialogDescription>
          Extracted data from the uploaded Kartu Keluarga document.
        </DialogDescription>
      </DialogHeader>

      <div v-if="data" class="flex gap-6 flex-1 overflow-hidden">
        <!-- Left Column: Data -->
        <div class="flex flex-col gap-6 flex-1 overflow-auto">
          <!-- Header Info -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 shrink-0">
            <Card>
              <CardHeader class="pb-2">
                <CardTitle class="text-sm font-medium text-muted-foreground">Family Head</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="text-lg font-bold">{{ data.extracted_content?.structured_data?.family_head_name }}</div>
                <div class="text-sm text-muted-foreground">No. KK: {{ data.extracted_content?.structured_data?.family_number }}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader class="pb-2">
                <CardTitle class="text-sm font-medium text-muted-foreground">Address</CardTitle>
              </CardHeader>
              <CardContent>
                <div class="text-sm">{{ data.extracted_content?.structured_data?.address }}</div>
                <div class="text-sm text-muted-foreground">
                  RT/RW: {{ data.extracted_content?.structured_data?.rt_rw }} | Village: {{ data.extracted_content?.structured_data?.village }}
                </div>
                <div class="text-sm text-muted-foreground">
                  District: {{ data.extracted_content?.structured_data?.district }} | City: {{ data.extracted_content?.structured_data?.city }}
                </div>
                <div class="text-sm text-muted-foreground">
                  Province: {{ data.extracted_content?.structured_data?.province }} | Postal Code: {{ data.extracted_content?.structured_data?.postal_code }}
                </div>
              </CardContent>
            </Card>
          </div>

          <Separator class="shrink-0" />

        <!-- Family Members Table -->
        <div class="flex flex-col overflow-auto min-h-0 flex-1">
          <h3 class="text-lg font-semibold mb-4 shrink-0">Family Members</h3>
          <div class="border rounded-md overflow-auto flex-1">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>NIK</TableHead>
                  <TableHead>Gender</TableHead>
                  <TableHead>Birth Date</TableHead>
                  <TableHead>Religion</TableHead>
                  <TableHead>Education</TableHead>
                  <TableHead>Occupation</TableHead>
                  <TableHead>Marital Status</TableHead>
                  <TableHead>Blood Type</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow v-for="member in data.extracted_content?.structured_data?.family_members" :key="member.nik">
                  <TableCell class="font-medium">{{ member.name }}</TableCell>
                  <TableCell>{{ member.nik }}</TableCell>
                  <TableCell>{{ member.gender }}</TableCell>
                  <TableCell>{{ formatDate(member.birth_date) }}</TableCell>
                  <TableCell>{{ member.religion }}</TableCell>
                  <TableCell>{{ member.education }}</TableCell>
                  <TableCell>{{ member.occupation }}</TableCell>
                  <TableCell>
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {{ member.marital_status }}
                    </span>
                  </TableCell>
                  <TableCell>{{ member.blood_type || '-' }}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </div>
        </div>

        <!-- Right Column: Document Preview -->
        <div class="w-1/3 flex flex-col shrink-0">
          <Card class="h-full flex flex-col">
            <CardHeader class="pb-3 shrink-0">
              <CardTitle class="text-sm font-medium text-muted-foreground">Document Preview</CardTitle>
            </CardHeader>
            <CardContent class="flex-1 overflow-auto p-2">
              <div v-if="data.url" class="w-full h-full bg-muted rounded-lg overflow-auto flex items-center justify-center">
                <img 
                  :src="data.url" 
                  :alt="data.name"
                  class="max-w-full max-h-full object-contain"
                />
              </div>
              <div v-else class="flex items-center justify-center h-full text-muted-foreground text-sm">
                No document preview available
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div v-else class="py-8 text-center text-muted-foreground">
        No structured data available for this document.
      </div>
    </DialogContent>
  </Dialog>
</template>
