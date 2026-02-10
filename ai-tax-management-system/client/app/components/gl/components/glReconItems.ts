import type { ColumnDef } from '@tanstack/vue-table'
import { h } from 'vue'
import type { GL } from '../data/schema'
import { BotIcon, UserPenIcon } from 'lucide-vue-next'

export const glReconColumns: ColumnDef<NonNullable<GL['glReconItem']>[number], any>[] = [
  // Auto-number column
  {
    id: 'index',
    header: 'No',
    cell: ({ row }) => h('div', { class: 'text-sm font-medium text-center' }, row.index + 1),
    enableSorting: false,
  },

  {
    accessorKey: 'itemName',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Item Name'),
    cell: ({ row }) => h('div', { class: 'text-sm break-words max-w-[200px] whitespace-normal', style: { wordWrap: 'break-word' } }, row.getValue('itemName')),
  },
  {
    accessorKey: 'typeOfTax',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Type of Tax'),
    cell: ({ row }) => 
      h
      (
        'div', 
        { 
          class: 'text-sm', 
          contenteditable: 'true',
          onInput: (e: Event) => {
            row.original.typeOfTax = (e.target as HTMLDivElement).innerText
          },
        }, 
        row.getValue('typeOfTax')
      ),
  },
  {
    accessorKey: 'taxBase',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Tax Base'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, row.getValue('taxBase')),
  },
  {
    accessorKey: 'rate',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Rate %'),
    cell: ({ row }) => {
      const rate = row.getValue<number>('rate')
      return h(
        'div',
        { class: 'text-sm text-right' },
        `${rate * 100}`
      )
    },
  },
  {
    accessorKey: 'whtNormal',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'WHT Normal'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, row.getValue('whtNormal')),
  },
  {
    accessorKey: 'remarks',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Remarks'),
    cell: ({ row }) => 
      h
      (
        'div', 
        { 
          class: 'text-sm', 
          contenteditable: 'true',
          onInput: (e: Event) => {
            row.original.remarks = (e.target as HTMLDivElement).innerText
          }, 
        }, 
        row.getValue('remarks')
      ),
  },
  {
    accessorKey: 'diffNormal',
    header: ({ column }) => h('div', { class: 'text-sm font-medium' }, 'Diff Normal'),
    cell: ({ row }) => h('div', { class: 'text-sm text-right' }, row.getValue('diffNormal') ?? '-'),
  },
  {
    accessorKey: 'checker',
    header: ({ column }) => h('div', { style: { width: '40px', textAlign: 'right' }, class: 'text-sm font-medium' }, ),
    enableSorting: false,
    cell: () =>
      h('div', { style: { width: '40px', textAlign: 'center' } }, 
        h(BotIcon, {
          width: '80px',
          size: 20,
          class: 'text-gray-600',
        })
      )
  },
]
