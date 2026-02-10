import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { statuses, types } from '../data/data'
import type { Job } from '../data/schema'
import DataTableColumnHeader from './DataTableColumnHeader.vue'
import DataTableRowActions from './DataTableRowActions.vue'

export const columns: ColumnDef<Job>[] = [
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
    accessorKey: 'title',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Title' }),
    cell: ({ row }) => h('div', { class: 'max-w-[200px] font-medium' }, row.getValue('title')),
  },
  {
    accessorKey: 'department',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Department' }),
    cell: ({ row }) => h('div', { class: 'text-sm text-muted-foreground' }, row.getValue('department')),
  },
  {
    accessorKey: 'location',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Location' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('location')),
  },
  {
    accessorKey: 'type',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Type' }),
    cell: ({ row }) => {
      const type = types.find(
        t => t.value === row.getValue('type'),
      )
      return h('div', { class: 'text-sm' }, type?.label || row.getValue('type'))
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
    accessorKey: 'applicants',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Applicants' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('applicants')),
  },
  {
    accessorKey: 'postedDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Posted Date' }),
    cell: ({ row }) => {
      const date = new Date(row.getValue('postedDate') as string)
      return h('div', { class: 'text-sm' }, date.toLocaleDateString())
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => h(DataTableRowActions, { row }),
  },
]
