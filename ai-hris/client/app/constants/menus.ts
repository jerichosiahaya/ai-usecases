import type { NavMenu, NavMenuItems } from '~/types/nav'

export const navMenu: NavMenu[] = [
  {
    heading: '',
    items: [
      {
        title: 'Home',
        icon: 'i-lucide-home',
        link: '/',
      }
    ],
  },
  {
    heading: 'Hiring',
    items: [
      {
        title: 'Jobs',
        icon: 'i-lucide-book-open',
        link: '/jobs',
      },
      // {
      //   title: 'Applicants',
      //   icon: 'i-lucide-file-user',
      //   link: '/applicants',
      // },
      {
        title: 'Candidates',
        icon: 'i-lucide-users',
        link: '/candidates',
      },
    ],
  },
  {
    heading: 'Internal',
    items: [
      {
        title: 'Employees',
        icon: 'i-lucide-users',
        link: '/employees',
      },
    ],
  }
]

export const navMenuBottom: NavMenuItems = []
