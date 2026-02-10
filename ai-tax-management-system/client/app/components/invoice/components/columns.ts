import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import type { Invoice } from '../data/schema'
import { formatNumber } from '@/components/gl/components/numbering'

export const invoiceDetailColumns: ColumnDef<NonNullable<Invoice['invoiceDetail']>[number], any>[] = [
  // Auto-number column
  {
    id: 'index',
    header: 'No',
    cell: ({ row }) => h('div', { class: 'text-sm font-medium text-center' }, row.index + 1),
    enableSorting: false,
  },

  {
    accessorKey: 'itemName',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Item/Service'),
    cell: ({ row }) => h('div', { class: 'text-sm break-words max-w-[200px] whitespace-normal', style: { wordWrap: 'break-word' } }, row.getValue('itemName')),
  },
  {
    accessorKey: 'quantity',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Quantity'),
    cell: ({ row }) => h('div', { class: 'text-sm text-muted-foreground' }, formatNumber(row.getValue('quantity'))),
  },
  {
    accessorKey: 'unitPrice',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Unit Price (Rp)'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('unitPrice'))),
  },
  {
    accessorKey: 'taxPercentage',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Tax %'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('taxPercentage'))),
  },
  {
    accessorKey: 'discountPercentage',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Discount %'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('discountPercentage'))),
  },
  {
    accessorKey: 'extendedPrice',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Extended Price (Rp)'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('extendedPrice'))),
  },
]
