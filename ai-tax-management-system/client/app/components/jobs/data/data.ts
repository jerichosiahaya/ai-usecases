import {
  CheckCircle2,
  Circle,
  HelpCircle,
  Timer,
  XCircle,
} from 'lucide-vue-next'

export const statuses = [
  {
    value: 'Open',
    label: 'Open',
    icon: CheckCircle2,
  },
  {
    value: 'Closed',
    label: 'Closed',
    icon: XCircle,
  },
  {
    value: 'Draft',
    label: 'Draft',
    icon: Circle,
  },
]

export const types = [
  {
    value: 'Full-time',
    label: 'Full-time',
  },
  {
    value: 'Part-time',
    label: 'Part-time',
  },
  {
    value: 'Contract',
    label: 'Contract',
  },
  {
    value: 'Internship',
    label: 'Internship',
  },
]
