<script setup lang="ts">
import type { Row } from '@tanstack/vue-table'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreHorizontalIcon, TrashIcon, EyeIcon, FileTextIcon } from 'lucide-vue-next'
import type { Employee } from '~/components/candidates/data/schema.js'


interface DataTableRowActionsProps {
  row: Row<Employee>
}

const props = defineProps<DataTableRowActionsProps>()
const router = useRouter()

const viewDetails = () => {
  console.log('Full row data:', props.row.original)
  console.log('Employee ID:', props.row.original.employee_id)
  console.log('Employee ID type:', typeof props.row.original.employee_id)

  navigateTo(`/employees/${props.row.original.employee_id}`)
}
const deleteRow = () => {
  console.log('Delete candidate:', props.row.original.employee_id)
  // Implement delete logic here
}

const downloadCV = () => {
  if (props.row?.original?.cv_url) {
    window.open(props.row?.original?.cv_url, '_blank')
  }
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
        <DropdownMenuItem v-if="row.original.cv_url" @click="downloadCV">
          <FileTextIcon class="mr-2 h-4 w-4" />
          Download CV
        </DropdownMenuItem>
        <DropdownMenuItem @click="deleteRow" class="text-red-600">
          <TrashIcon class="mr-2 h-4 w-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>
