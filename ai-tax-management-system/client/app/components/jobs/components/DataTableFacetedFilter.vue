<script setup lang="ts">
import type { Column } from '@tanstack/vue-table'
import { computed } from 'vue'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { Badge } from '@/components/ui/badge'
import { CheckIcon, PlusCircleIcon } from 'lucide-vue-next'
import { cn } from '@/lib/utils'

interface DataTableFacetedFilterProps {
  column: Column<any, any>
  title?: string
  options: {
    label: string
    value: string
    icon?: any
  }[]
  table?: any
}

const props = defineProps<DataTableFacetedFilterProps>()

const selectedValues = computed(() => {
  return new Set(props.column?.getFilterValue() as string[])
})

const handleSelect = (value: string) => {
  const isSelected = selectedValues.value.has(value)
  if (isSelected) {
    selectedValues.value.delete(value)
  } else {
    selectedValues.value.add(value)
  }
  props.column.setFilterValue(
    Array.from(selectedValues.value).length > 0
      ? Array.from(selectedValues.value)
      : undefined,
  )
}
</script>

<template>
  <Popover>
    <PopoverTrigger as-child>
      <Button variant="outline" size="sm" class="h-10 border-dashed">
        <PlusCircleIcon class="mr-2 h-4 w-4" />
        {{ title }}
        <template v-if="selectedValues.size > 0">
          <div class="ml-2 hidden space-x-1 lg:flex">
            <Badge v-if="selectedValues.size > 2" variant="secondary" class="rounded-sm px-1 font-normal">
              {{ selectedValues.size }} selected
            </Badge>
            <template v-else>
              <Badge v-for="option in options.filter(option => selectedValues.has(option.value))" :key="option.value" variant="secondary" class="rounded-sm px-1 font-normal">
                {{ option.label }}
              </Badge>
            </template>
          </div>
        </template>
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[200px] p-0" align="start">
      <Command>
        <CommandInput :placeholder="`Filter ${title}...`" />
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandList>
          <CommandGroup>
            <CommandItem
              v-for="option in options"
              :key="option.value"
              :value="option.value"
              @select="handleSelect(option.value)"
            >
              <div
                :class="cn(
                  'mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary',
                  selectedValues.has(option.value)
                    ? 'bg-primary text-primary-foreground'
                    : 'opacity-50 [&_svg]:invisible',
                )"
              >
                <CheckIcon class="h-4 w-4" />
              </div>
              <span>{{ option.label }}</span>
            </CommandItem>
          </CommandGroup>
        </CommandList>
        <CommandSeparator v-if="selectedValues.size > 0" />
        <CommandList v-if="selectedValues.size > 0">
          <CommandGroup>
            <CommandItem
              value="clear-filters"
              class="justify-center text-center"
              @select="props.column.setFilterValue(undefined)"
            >
              Clear filters
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>
