<script setup lang="ts">
import type { Table } from '@tanstack/vue-table'
import type { Candidate } from '../data/schema'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { statuses, positions } from '../data/data'
import DataTableFacetedFilter from './DataTableFacetedFilter.vue'
import DataTableViewOptions from './DataTableViewOptions.vue'

interface DataTableToolbarProps {
  table: Table<Candidate>
}

const props = defineProps<DataTableToolbarProps>()

const isFilterActive = computed(() => props.table.getState().columnFilters.length > 0)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex flex-1 flex-col gap-2 lg:flex-row lg:items-center lg:gap-2">
        <Input
          placeholder="Filter by name..."
          :model-value="(props.table.getColumn('name')?.getFilterValue() as string) ?? ''"
          class="h-10 w-full lg:max-w-sm"
          @update:model-value="props.table.getColumn('name')?.setFilterValue($event)"
        />
        <DataTableFacetedFilter
          v-if="props.table.getColumn('position')"
          :column="(props.table.getColumn('position') as any)"
          title="Position"
          :options="positions"
          :table="props.table"
        />
        <DataTableFacetedFilter
          v-if="props.table.getColumn('status')"
          :column="(props.table.getColumn('status') as any)"
          title="Status"
          :options="statuses.map(s => ({ label: s.label, value: s.value }))"
          :table="props.table"
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
