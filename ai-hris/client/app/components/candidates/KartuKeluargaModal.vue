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
    <DialogContent class="max-w-4xl max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Kartu Keluarga Details</DialogTitle>
        <DialogDescription>
          Extracted data from the uploaded Kartu Keluarga document.
        </DialogDescription>
      </DialogHeader>

      <div v-if="data" class="space-y-6">
        <!-- Header Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">Family Head</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="text-lg font-bold">{{ data.extractedContent?.structured_data?.family_head_name }}</div>
              <div class="text-sm text-muted-foreground">No. KK: {{ data.extractedContent?.structured_data?.family_number }}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="pb-2">
              <CardTitle class="text-sm font-medium text-muted-foreground">Address</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="text-sm">{{ data.extractedContent?.structured_data?.address }}</div>
              <div class="text-sm text-muted-foreground">
                RT/RW: {{ data.extractedContent?.structured_data?.rt_rw }} | Village: {{ data.extractedContent?.structured_data?.village }}
              </div>
              <div class="text-sm text-muted-foreground">
                District: {{ data.extractedContent?.structured_data?.district }} | City: {{ data.extractedContent?.structured_data?.city }}
              </div>
              <div class="text-sm text-muted-foreground">
                Province: {{ data.extractedContent?.structured_data?.province }} | Postal Code: {{ data.extractedContent?.structured_data?.postal_code }}
              </div>
            </CardContent>
          </Card>
        </div>

        <Separator />

        <!-- Family Members Table -->
        <div>
          <h3 class="text-lg font-semibold mb-4">Family Members</h3>
          <div class="border rounded-md">
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
                <TableRow v-for="member in data.extractedContent?.structured_data?.family_members" :key="member.nik">
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
      
      <div v-else class="py-8 text-center text-muted-foreground">
        No structured data available for this document.
      </div>
    </DialogContent>
  </Dialog>
</template>
