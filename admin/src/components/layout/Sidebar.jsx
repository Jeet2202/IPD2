import React from 'react';
import { ChevronLeft, ChevronRight, Wrench, X } from 'lucide-react';
import { NAVIGATION_ITEMS } from '../../constants/navigation';
import SidebarItem from './SidebarItem';

export default function Sidebar({
  isCollapsed,
  onToggleCollapse,
  isMobileOpen,
  onCloseMobile,
}) {
  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-[#0F172A]/50 backdrop-blur-xs z-40 lg:hidden transition-opacity duration-300"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 bg-white border-r border-[#E2E8F0] flex flex-col transition-all duration-300 ease-in-out ${
          isCollapsed ? 'w-20' : 'w-64'
        } ${
          isMobileOpen
            ? 'translate-x-0 w-64'
            : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Sidebar Header */}
        <div className="h-16 border-b border-[#F1F5F9] flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#2563EB] to-[#0EA5E9] flex items-center justify-center text-white shadow-sm shadow-[#2563EB]/30 shrink-0">
              <Wrench className="w-5 h-5" />
            </div>

            {(!isCollapsed || isMobileOpen) && (
              <div className="flex flex-col truncate">
                <span className="text-base font-extrabold text-[#0F172A] tracking-tight leading-none">
                  KaamSetu
                </span>
                <span className="text-[11px] font-semibold text-[#64748B] tracking-wide mt-1">
                  Admin Panel
                </span>
              </div>
            )}
          </div>

          {/* Mobile Close Button */}
          <button
            onClick={onCloseMobile}
            className="p-1.5 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Desktop Collapse Button */}
          <button
            onClick={onToggleCollapse}
            className="hidden lg:flex p-1.5 rounded-lg text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] transition-colors"
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Sidebar Navigation Items */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {NAVIGATION_ITEMS.map((group, idx) => (
            <div key={idx} className="space-y-1">
              {(!isCollapsed || isMobileOpen) && (
                <h3 className="px-3 text-[10px] font-bold text-[#94A3B8] tracking-wider uppercase mb-2">
                  {group.section}
                </h3>
              )}
              {group.items.map((item) => (
                <SidebarItem
                  key={item.path}
                  item={item}
                  isCollapsed={isCollapsed && !isMobileOpen}
                  onItemClick={onCloseMobile}
                />
              ))}
            </div>
          ))}
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-[#F1F5F9] shrink-0">
          <div
            className={`flex items-center gap-3 p-2 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]/60 ${
              isCollapsed && !isMobileOpen ? 'justify-center p-2' : ''
            }`}
          >
            <div className="w-2.5 h-2.5 rounded-full bg-[#16A34A] animate-pulse shrink-0" />
            {(!isCollapsed || isMobileOpen) && (
              <div className="flex flex-col truncate">
                <span className="text-[11px] font-bold text-[#0F172A]">
                  System Live
                </span>
                <span className="text-[10px] text-[#64748B]">v1.0.0 Stable</span>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
