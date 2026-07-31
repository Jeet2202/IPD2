import {
  LayoutDashboard,
  Users,
  HardHat,
  BadgeCheck,
  Layers,
  Wrench,
  IndianRupee,
  ClipboardList,
  SearchCheck,
  FileText,
  ShieldAlert,
  Percent,
  CreditCard,
  Wallet,
  RotateCcw,
  MessageSquareWarning,
  Star,
  Bell,
  BarChart3,
  FileChartColumn,
  ScrollText,
  ShieldCheck,
  Settings,
} from 'lucide-react';

export const NAVIGATION_ITEMS = [
  {
    section: 'DASHBOARD',
    items: [
      {
        name: 'Dashboard',
        path: '/admin/dashboard',
        icon: LayoutDashboard,
      },
    ],
  },
  {
    section: 'MANAGEMENT',
    items: [
      {
        name: 'Customers',
        path: '/admin/customers',
        icon: Users,
      },
      {
        name: 'Workers',
        path: '/admin/workers',
        icon: HardHat,
      },
      {
        name: 'Worker Verification',
        path: '/admin/verifications',
        icon: BadgeCheck,
      },
    ],
  },
  {
    section: 'SERVICES & PRICING',
    items: [
      {
        name: 'Service Categories',
        path: '/admin/service-categories',
        icon: Layers,
      },
      {
        name: 'Services',
        path: '/admin/services',
        icon: Wrench,
      },
      {
        name: 'Market Price Guide',
        path: '/admin/pricing',
        icon: IndianRupee,
      },
    ],
  },
  {
    section: 'OPERATIONS',
    items: [
      {
        name: 'Jobs',
        path: '/admin/jobs',
        icon: ClipboardList,
      },
      {
        name: 'Inspection Requests',
        path: '/admin/inspections',
        icon: SearchCheck,
      },
      {
        name: 'Inspection Reports',
        path: '/admin/inspection-reports',
        icon: FileText,
      },
      {
        name: 'Flagged Pricing',
        path: '/admin/flagged-pricing',
        icon: ShieldAlert,
      },
      {
        name: 'Inspection Conversions',
        path: '/admin/inspection-conversions',
        icon: Percent,
      },
      {
        name: 'Quotations',
        path: '/admin/quotations',
        icon: FileText,
      },
    ],
  },
  {
    section: 'FINANCE',
    items: [
      {
        name: 'Payments',
        path: '/admin/payments',
        icon: CreditCard,
      },
      {
        name: 'Transactions',
        path: '/admin/transactions',
        icon: ScrollText,
      },
      {
        name: 'Worker Payouts',
        path: '/admin/payouts',
        icon: Wallet,
      },
      {
        name: 'Refunds',
        path: '/admin/refunds',
        icon: RotateCcw,
      },
      {
        name: 'Revenue & Commission',
        path: '/admin/revenue',
        icon: BarChart3,
      },
    ],
  },
  {
    section: 'SUPPORT',
    items: [
      {
        name: 'Complaints',
        path: '/admin/complaints',
        icon: MessageSquareWarning,
      },
      {
        name: 'Reviews',
        path: '/admin/reviews',
        icon: Star,
      },
      {
        name: 'Notifications',
        path: '/admin/notifications',
        icon: Bell,
      },
    ],
  },
  {
    section: 'SYSTEM',
    items: [
      {
        name: 'Analytics',
        path: '/admin/analytics',
        icon: BarChart3,
      },
      {
        name: 'Reports',
        path: '/admin/reports',
        icon: FileChartColumn,
      },
      {
        name: 'Audit Logs',
        path: '/admin/audit-logs',
        icon: ScrollText,
      },
      {
        name: 'Admin Users',
        path: '/admin/admins',
        icon: ShieldCheck,
      },
      {
        name: 'Settings',
        path: '/admin/settings',
        icon: Settings,
      },
    ],
  },
];
