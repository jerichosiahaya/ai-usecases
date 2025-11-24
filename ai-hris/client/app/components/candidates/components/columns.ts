import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { statuses, positions } from '../data/data'
import type { Candidate } from '../data/schema'
import DataTableColumnHeader from './DataTableColumnHeader.vue'
import DataTableRowActions from './DataTableRowActions.vue'

export const columns: ColumnDef<Candidate>[] = [
  {
    id: 'select',
    header: ({ table }) => h(Checkbox, {
      'checked': table.getIsAllPageRowsSelected() || (table.getIsSomePageRowsSelected() && 'indeterminate'),
      'onUpdate:checked': (value: any) => table.toggleAllPageRowsSelected(!!value),
      'ariaLabel': 'Select all',
      'class': 'translate-y-0.5',
    }),
    cell: ({ row }) => h(Checkbox, { 'checked': row.getIsSelected(), 'onUpdate:checked': (value: any) => row.toggleSelected(!!value), 'ariaLabel': 'Select row', 'class': 'translate-y-0.5' }),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'name',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Name' }),
    cell: ({ row }) => h('div', { class: 'max-w-[200px] font-medium' }, row.getValue('name')),
  },
  {
    accessorKey: 'email',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Email' }),
    cell: ({ row }) => h('div', { class: 'text-sm text-muted-foreground' }, row.getValue('email')),
  },
  {
    accessorKey: 'position',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Position' }),
    cell: ({ row }) => {
      const position = positions.find(
        pos => pos.value === row.getValue('position'),
      )
      return h('div', { class: 'text-sm' }, position?.label || row.getValue('position'))
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Status' }),
    cell: ({ row }) => {
      const status = statuses.find(
        status => status.value === row.getValue('status'),
      )

      if (!status)
        return null

      return h('div', { class: 'flex items-center gap-2' }, [
        status.icon && h(status.icon, { class: 'h-4 w-4' }),
        h('span', { class: 'text-sm' }, status.label),
      ])
    },
    filterFn: (row, id, value) => {
      return value.includes(row.getValue(id))
    },
  },
  {
    accessorKey: 'experience',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Experience' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, `${row.getValue('experience')} yrs`),
  },
  {
    accessorKey: 'rating',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Rating' }),
    cell: ({ row }) => {
      const rating = row.getValue('rating') as number | undefined
      return h('div', { class: 'flex items-center gap-1' }, [
        h('span', { class: 'text-sm font-medium' }, rating?.toFixed(1) || 'N/A'),
        h('span', { class: 'text-xs text-muted-foreground' }, '⭐'),
      ])
    },
  },
  {
    accessorKey: 'appliedDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Applied Date' }),
    cell: ({ row }) => {
      const date = new Date(row.getValue('appliedDate') as string)
      return h('div', { class: 'text-sm' }, date.toLocaleDateString())
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => h(DataTableRowActions, { row }),
  },
]
