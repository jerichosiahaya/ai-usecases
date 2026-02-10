import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import type { TaxInvoice } from '../data/schema'
import { formatNumber } from '~/components/gl/components/numbering'

export const taxInvoiceDetailColumns: ColumnDef<NonNullable<TaxInvoice['taxInvoiceDetail']>[number], any>[] = [
  // Auto-number column
  {
    id: 'index',
    header: 'No',
    cell: ({ row }) => h('div', { class: 'text-sm font-medium text-center' }, row.index + 1),
    enableSorting: false,
  },
  {
    accessorKey: 'itemCode',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Kode Barang/Jasa'),
    cell: ({ row }) => h('div', { class: 'text-sm break-words max-w-[200px] whitespace-normal', style: { wordWrap: 'break-word' } }, row.getValue('itemCode')),
  },
  {
    accessorKey: 'itemName',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Nama Barang Kena Pajak / Jasa Kena Pajak'),
    cell: ({ row }) => h('div', { class: 'text-sm text-muted-foreground' }, row.getValue('itemName')),
  },
  {
    accessorKey: 'quantity',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Quantity'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('quantity'))),
  },
  {
    accessorKey: 'price',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Unit Price (Rp)'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('price'))),
  },
  {
    accessorKey: 'taxBaseWht',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Harga Jual/Penggantian/Uang Muka/Termin'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, formatNumber(row.getValue('taxBaseWht'))),
  },
]
