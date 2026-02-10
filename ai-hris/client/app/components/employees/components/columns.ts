import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
// import { statuses, positions } from '../data/data'
import type { Employee } from '~/components/candidates/data/schema'
import DataTableRowActions from './DataTableRowActions.vue'
import DataTableColumnHeader from './DataTableColumnHeader.vue'

export const columns: ColumnDef<Employee>[] = [
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
  // {
  //   accessorKey: 'position',
  //   header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Position' }),
  //   cell: ({ row }) => {
  //     const position = positions.find(
  //       pos => pos.value === row.getValue('position'),
  //     )
  //     return h('div', { class: 'text-sm' }, position?.label || row.getValue('position'))
  //   },
  //   filterFn: (row, id, value) => {
  //     return value.includes(row.getValue(id))
  //   },
  // },
  // {
  //   accessorKey: 'status',
  //   header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Status' }),
  //   cell: ({ row }) => {
  //     const status = statuses.find(
  //       status => status.value === row.getValue('status'),
  //     )

  //     if (!status)
  //       return null

  //     const colors: Record<string, string> = {
  //       applied: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700',
  //       reviewing: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800',
  //       shortlisted: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200 dark:border-purple-800',
  //       rejected: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800',
  //       hired: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border-green-200 dark:border-green-800',
  //     }

  //     return h(Badge, {
  //       variant: 'outline',
  //       class: `flex w-fit items-center gap-1.5 px-2 py-0.5 ${colors[status.value] || ''}`
  //     }, () => [
  //       status.icon && h(status.icon, { class: 'h-3.5 w-3.5' }),
  //       status.label,
  //     ])
  //   },
  //   filterFn: (row, id, value) => {
  //     return value.includes(row.getValue(id))
  //   },
  // },
  {
    id: 'experience',
    accessorFn: (row) => {
      const workExperiences = row.work_experiences || []
      if (workExperiences.length === 0) {
        return row.experience || 0
      }
      const totalMilliseconds = workExperiences.reduce((acc, exp) => {
        const startDate = new Date(exp.start_date).getTime()
        const endDate = exp.end_date ? new Date(exp.end_date).getTime() : Date.now()
        return acc + (endDate - startDate)
      }, 0)
      return totalMilliseconds / (1000 * 60 * 60 * 24 * 365.25)
    },
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Experience' }),
    cell: ({ row }) => {
      const years = row.getValue('experience') as number
      return h('div', { class: 'text-sm' }, `${years.toFixed(1)} yrs`)
    },
  },
  // {
  //   accessorKey: 'rating',
  //   header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Rating' }),
  //   cell: ({ row }) => {
  //     const rating = row.getValue('rating') as number | undefined
  //     return h('div', { class: 'flex items-center gap-1' }, [
  //       h('span', { class: 'text-sm font-medium' }, rating?.toFixed(1) || 'N/A'),
  //       h('span', { class: 'text-xs text-muted-foreground' }, '⭐'),
  //     ])
  //   },
  // },
  {
    accessorKey: 'joined_date',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Joined Date' }),
    cell: ({ row }) => {
      const date = new Date(row.getValue('joined_date') as string)
      return h('div', { class: 'text-sm' }, date.toLocaleDateString())
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => h(DataTableRowActions, { row }),
  },
]
