<script setup lang="ts">
import type { Row } from '@tanstack/vue-table'
import type { GL } from '../data/schema'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreHorizontalIcon, TrashIcon, EyeIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

interface DataTableRowActionsProps {
  row: Row<GL>
}

const props = defineProps<DataTableRowActionsProps>()
const router = useRouter()

const viewDetails = () => {
  router.push(`/gl/${props.row.original.urn}`)
}

const deleteRow = () => {
  console.log('Delete job:', props.row.original.urn)
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
        <DropdownMenuItem @click="deleteRow" class="text-red-600">
          <TrashIcon class="mr-2 h-4 w-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>
