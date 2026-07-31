import React from 'react';
import { NavLink } from 'react-router-dom';
import { IndianRupee, Home, TrendingUp, ShieldAlert } from 'lucide-react';

export default function PricingNavTabs() {
  const navTabs = [
    {
      name: 'Market Price Guide',
      path: '/admin/pricing',
      exact: true,
      icon: IndianRupee,
    },
    {
      name: 'Visiting Charges',
      path: '/admin/pricing/visiting-charges',
      icon: Home,
    },
    {
      name: 'Customer Price Options',
      path: '/admin/pricing/price-increase',
      icon: TrendingUp,
    },
    {
      name: 'Price Tolerance Rules',
      path: '/admin/pricing/tolerance',
      icon: ShieldAlert,
    },
  ];

  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-1.5 shadow-xs mb-6 overflow-x-auto">
      <div className="flex items-center gap-1.5 min-w-max">
        {navTabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <NavLink
              key={tab.path}
              to={tab.path}
              end={tab.exact}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all duration-150 ${
                  isActive
                    ? 'bg-[#2563EB] text-white shadow-xs'
                    : 'text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC]'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{tab.name}</span>
            </NavLink>
          );
        })}
      </div>
    </div>
  );
}
