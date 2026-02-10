<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { ArrowDownIcon, ArrowUpIcon, ChevronsUpDownIcon, EyeOffIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

interface DataTableColumnHeaderProps {
  column?: Column<any, any>
  title?: string
}

const props = defineProps<DataTableColumnHeaderProps>()
</script>

<template>
  <div v-if="props.column?.getCanSort()" :class="cn('flex items-center space-x-2', props.column?.getCanSort() && 'cursor-pointer select-none')">
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <Button
          variant="ghost"
          size="sm"
          class="h-10 -ml-3 data-[state=open]:bg-accent"
        >
          <span>{{ props.title }}</span>
          <template v-if="props.column?.getIsSorted() === 'desc'">
            <ArrowDownIcon class="ml-2 h-4 w-4" />
          </template>
          <template v-else-if="props.column?.getIsSorted() === 'asc'">
            <ArrowUpIcon class="ml-2 h-4 w-4" />
          </template>
          <template v-else>
            <ChevronsUpDownIcon class="ml-2 h-4 w-4" />
          </template>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        <DropdownMenuItem @click="props.column?.toggleSorting(false)">
          <ArrowUpIcon class="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
          Asc
        </DropdownMenuItem>
        <DropdownMenuItem @click="props.column?.toggleSorting(true)">
          <ArrowDownIcon class="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
          Desc
        </DropdownMenuItem>
        <DropdownMenuItem v-if="props.column?.getCanHide()" @click="props.column?.toggleVisibility(false)">
          <EyeOffIcon class="mr-2 h-3.5 w-3.5 text-muted-foreground/70" />
          Hide
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
  <div v-else>
    {{ props.title }}
  </div>
</template>
