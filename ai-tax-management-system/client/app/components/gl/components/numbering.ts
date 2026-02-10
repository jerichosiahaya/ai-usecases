export function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined ) return '-'
  return new Intl.NumberFormat('id-ID', {useGrouping: true}).format(value)
}
