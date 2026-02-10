<script setup lang="ts">
import type { Row } from '@tanstack/vue-table'
import type { Job } from '../data/schema'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreHorizontalIcon, TrashIcon, EyeIcon, EditIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

interface DataTableRowActionsProps {
  row: Row<Job>
}

const props = defineProps<DataTableRowActionsProps>()
const router = useRouter()

const viewDetails = () => {
  router.push(`/jobs/${props.row.original.id}`)
}

const editJob = () => {
  console.log('Edit job:', props.row.original.id)
}

const deleteRow = () => {
  console.log('Delete job:', props.row.original.id)
}
</script>

<template>
  <div>
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <Button variant="ghost" class="h-8 w-8 p-0">
          <span class="sr-only">Open menu</span>
          <MoreHorizontalIcon class="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem @click="viewDetails">
          <EyeIcon class="mr-2 h-4 w-4" />
          View Details
        </DropdownMenuItem>
        <DropdownMenuItem @click="editJob">
          <EditIcon class="mr-2 h-4 w-4" />
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem @click="deleteRow" class="text-red-600">
          <TrashIcon class="mr-2 h-4 w-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>
