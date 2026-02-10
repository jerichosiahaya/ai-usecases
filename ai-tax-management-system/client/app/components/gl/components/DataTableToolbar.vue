<script setup lang="ts">
import type { Table } from '@tanstack/vue-table'
import type { GL } from '../data/schema'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import DataTableFacetedFilter from './DataTableFacetedFilter.vue'
import DataTableViewOptions from './DataTableViewOptions.vue'
import { computed } from 'vue'

interface DataTableToolbarProps {
  table: Table<GL>
}

const props = defineProps<DataTableToolbarProps>()

const isFilterActive = computed(() => props.table.getState().columnFilters.length > 0)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex flex-1 flex-col gap-2 lg:flex-row lg:items-center lg:gap-2">
        <Input
          placeholder="Filter by URN..."
          :model-value="(props.table.getColumn('urn')?.getFilterValue() as string) ?? ''"
          class="h-10 w-full lg:max-w-sm"
          @update:model-value="props.table.getColumn('urn')?.setFilterValue($event)"
        />
      </div>
      <div class="flex gap-2">
        <DataTableViewOptions :table="props.table" />
        <Button
          v-if="isFilterActive"
          variant="ghost"
          size="sm"
          @click="props.table.resetColumnFilters()"
        >
          Clear filters
        </Button>
      </div>
    </div>
  </div>
</template>
