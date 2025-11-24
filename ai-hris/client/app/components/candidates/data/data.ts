import { CircleCheckIcon, CircleXIcon, FileIcon, HourglassIcon, StarIcon } from 'lucide-vue-next'

export const statuses = [
  {
    value: 'applied',
    label: 'Applied',
    icon: FileIcon,
  },
  {
    value: 'reviewing',
    label: 'Reviewing',
    icon: HourglassIcon,
  },
  {
    value: 'shortlisted',
    label: 'Shortlisted',
    icon: StarIcon,
  },
  {
    value: 'rejected',
    label: 'Rejected',
    icon: CircleXIcon,
  },
  {
    value: 'hired',
    label: 'Hired',
    icon: CircleCheckIcon,
  },
]

export const positions = [
  {
    label: 'Frontend Developer',
    value: 'frontend-developer',
  },
  {
    label: 'Backend Developer',
    value: 'backend-developer',
  },
  {
    label: 'Full Stack Developer',
    value: 'full-stack-developer',
  },
  {
    label: 'Data Scientist',
    value: 'data-scientist',
  },
  {
    label: 'DevOps Engineer',
    value: 'devops-engineer',
  },
  {
    label: 'Product Manager',
    value: 'product-manager',
  },
  {
    label: 'UX/UI Designer',
    value: 'ux-ui-designer',
  },
  {
    label: 'HR Manager',
    value: 'hr-manager',
  },
]

export const experienceLevels = [
  {
    label: 'Entry Level (0-2 years)',
    value: 'entry',
  },
  {
    label: 'Mid Level (2-5 years)',
    value: 'mid',
  },
  {
    label: 'Senior (5+ years)',
    value: 'senior',
  },
]
