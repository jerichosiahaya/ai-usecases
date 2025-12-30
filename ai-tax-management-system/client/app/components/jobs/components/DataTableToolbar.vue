<script setup lang="ts">
import type { Table } from '@tanstack/vue-table'
import type { Job } from '../data/schema'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { statuses, types } from '../data/data'
import DataTableFacetedFilter from './DataTableFacetedFilter.vue'
import DataTableViewOptions from './DataTableViewOptions.vue'
import { computed } from 'vue'

interface DataTableToolbarProps {
  table: Table<Job>
}

const props = defineProps<DataTableToolbarProps>()

const isFilterActive = computed(() => props.table.getState().columnFilters.length > 0)
</script>

<template>
  <div class="flex flex-col gap-4">
    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex flex-1 flex-col gap-2 lg:flex-row lg:items-center lg:gap-2">
        <Input
          placeholder="Filter by title..."
          :model-value="(props.table.getColumn('title')?.getFilterValue() as string) ?? ''"
          class="h-10 w-full lg:max-w-sm"
          @update:model-value="props.table.getColumn('title')?.setFilterValue($event)"
        />
        <DataTableFacetedFilter
          v-if="props.table.getColumn('type')"
          :column="(props.table.getColumn('type') as any)"
          title="Type"
          :options="types"
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
