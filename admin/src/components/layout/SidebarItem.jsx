import React from 'react';
import { NavLink } from 'react-router-dom';

export default function SidebarItem({ item, isCollapsed, onItemClick }) {
  const Icon = item.icon;

  return (
    <NavLink
      to={item.path}
      onClick={onItemClick}
      className={({ isActive }) =>
        `group relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
          isActive
            ? 'bg-[#2563EB] text-white shadow-sm shadow-[#2563EB]/30'
            : 'text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9]'
        } ${isCollapsed ? 'justify-center px-2' : ''}`
      }
      title={isCollapsed ? item.name : undefined}
    >
      <Icon className={`w-4 h-4 shrink-0 transition-transform duration-200 group-hover:scale-110`} />
      {!isCollapsed && (
        <span className="truncate tracking-wide flex-1">{item.name}</span>
      )}
      {!isCollapsed && item.badge && (
        <span className="text-[8px] font-black px-1.5 py-0.5 rounded-full bg-[#7C3AED] text-white animate-pulse shrink-0">
          {item.badge}
        </span>
      )}

      {/* Tooltip for collapsed desktop view */}
      {isCollapsed && (
        <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-[#0F172A] text-white text-[11px] font-medium rounded-md opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50 whitespace-nowrap shadow-md">
          {item.name}
        </div>
      )}
    </NavLink>
  );
}
