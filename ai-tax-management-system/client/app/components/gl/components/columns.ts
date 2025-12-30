import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import type { GL } from '../data/schema'
import DataTableColumnHeader from './DataTableColumnHeader.vue'
import DataTableRowActions from './DataTableRowActions.vue'

export const columns: ColumnDef<GL>[] = [
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
    accessorKey: 'urn',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'URN' }),
    cell: ({ row }) => h('div', { class: 'max-w-[200px] font-medium' }, row.getValue('urn')),
  },
  {
    accessorKey: 'vendorId',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Vendor Id' }),
    cell: ({ row }) => h('div', { class: 'text-sm text-muted-foreground' }, row.getValue('vendorId')),
  },
  {
    accessorKey: 'referenceNumber',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Reference Number' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('referenceNumber')),
  },
  {
    accessorKey: 'documentNumber',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Document umber' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('documentNumber')),
  },
  {
    accessorKey: 'poNumber',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'PO Number' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('poNumber')),
  },
  {
    accessorKey: 'documentDate',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Document Date' }),
    cell: ({ row }) => {
      const date = new Date(row.getValue('documentDate') as string)
      return h('div', { class: 'text-sm' }, date.toLocaleDateString())
    },
  },
  {
    accessorKey: 'diffNormal',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Diff Normal' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('diffNormal')),
  },
  {
    accessorKey: 'ref',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Ref' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('ref')),
  },
  {
    accessorKey: 'firstVouching',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'First Vouching' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('firstVouching')),
  },
  {
    accessorKey: 'secondReviewer',
    header: ({ column }) => h(DataTableColumnHeader, { column, title: 'Second Reviewer' }),
    cell: ({ row }) => h('div', { class: 'text-sm' }, row.getValue('secondReviewer')),
  },
  {
    id: 'actions',
    cell: ({ row }) => h(DataTableRowActions, { row }),
  },
]
