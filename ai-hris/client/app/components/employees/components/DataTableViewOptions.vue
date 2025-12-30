<script setup lang="ts">
import type { Table } from '@tanstack/vue-table'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { MoreHorizontalIcon } from 'lucide-vue-next'

interface DataTableViewOptionsProps {
  table: Table<any>
}

defineProps<DataTableViewOptionsProps>()
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" size="sm" class="ml-auto h-10 lg:flex">
        <MoreHorizontalIcon class="mr-2 h-4 w-4" />
        View
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-[150px]">
      <DropdownMenuCheckboxItem v-for="column in table
        .getAllColumns()
        .filter(column => typeof column.accessorFn !== 'undefined' && column.getCanHide())" :key="column.id"
        class="capitalize" :checked="column.getIsVisible()"
        @update:checked="(value: any) => column.toggleVisibility(!!value)">
        {{ column.id }}
      </DropdownMenuCheckboxItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
