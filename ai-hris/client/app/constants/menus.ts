import type { NavMenu, NavMenuItems } from '~/types/nav'

export const navMenu: NavMenu[] = [
  {
    heading: 'General',
    items: [
      {
        title: 'Home',
        icon: 'i-lucide-home',
        link: '/',
      },
      {
        title: 'Jobs',
        icon: 'i-lucide-book-open',
        link: '/jobs',
      },
      {
        title: 'Candidates',
        icon: 'i-lucide-users',
        link: '/candidates',
      },
    ],
  }
]

export const navMenuBottom: NavMenuItems = []
