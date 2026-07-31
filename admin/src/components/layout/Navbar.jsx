import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Menu,
  Search,
  Bell,
  ChevronDown,
  User,
  Settings as SettingsIcon,
  LogOut,
  Shield,
} from 'lucide-react';
import { NAVIGATION_ITEMS } from '../../constants/navigation';

export default function Navbar({ onOpenMobileSidebar }) {
  const location = useLocation();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close profile dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsProfileOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Compute page title dynamically from route
  const getPageTitle = () => {
    for (const group of NAVIGATION_ITEMS) {
      for (const item of group.items) {
        if (item.path === location.pathname) {
          return item.name;
        }
      }
    }
    return 'Dashboard';
  };

  return (
    <header className="h-16 bg-white border-b border-[#E2E8F0] sticky top-0 z-30 px-4 lg:px-8 flex items-center justify-between gap-4">
      {/* Left: Mobile Toggle & Page Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="p-2 rounded-xl text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] lg:hidden"
          aria-label="Open menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex flex-col">
          <h1 className="text-base lg:text-lg font-bold text-[#0F172A] tracking-tight">
            {getPageTitle()}
          </h1>
        </div>
      </div>

      {/* Center: Global Search Bar */}
      <div className="hidden md:flex flex-1 max-w-md mx-4">
        <div className="relative w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
          <input
            type="text"
            placeholder="Search customers, workers, jobs..."
            className="w-full pl-10 pr-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] placeholder-[#94A3B8] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB] transition-all"
          />
        </div>
      </div>

      {/* Right: Notifications & Profile */}
      <div className="flex items-center gap-3">
        {/* Notification Button */}
        <button
          className="relative p-2 rounded-xl text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#EF4444] rounded-full ring-2 ring-white" />
        </button>

        <div className="h-6 w-px bg-[#E2E8F0] mx-1" />

        {/* Admin Profile Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setIsProfileOpen(!isProfileOpen)}
            className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-[#F1F5F9] transition-colors"
            aria-expanded={isProfileOpen}
            aria-haspopup="true"
          >
            <div className="w-8 h-8 rounded-lg bg-[#2563EB] text-white flex items-center justify-center font-extrabold text-xs shadow-xs">
              A
            </div>
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-xs font-bold text-[#0F172A] leading-none">
                Admin
              </span>
              <span className="text-[10px] font-semibold text-[#64748B] mt-0.5">
                Super Admin
              </span>
            </div>
            <ChevronDown className="w-4 h-4 text-[#64748B]" />
          </button>

          {/* Profile Dropdown Menu */}
          {isProfileOpen && (
            <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl border border-[#E2E8F0] shadow-xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-2.5 border-b border-[#F1F5F9]">
                <p className="text-xs font-bold text-[#0F172A]">Admin Account</p>
                <p className="text-[11px] text-[#64748B] mt-0.5">admin@kaamsetu.com</p>
                <div className="mt-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-[10px] font-bold">
                  <Shield className="w-3 h-3" />
                  Super Admin
                </div>
              </div>

              <div className="py-1">
                <button
                  onClick={() => setIsProfileOpen(false)}
                  className="w-full px-4 py-2 text-left text-xs text-[#475569] hover:text-[#0F172A] hover:bg-[#F8FAFC] flex items-center gap-2.5 font-medium transition-colors"
                >
                  <User className="w-4 h-4 text-[#64748B]" />
                  My Profile
                </button>
                <button
                  onClick={() => setIsProfileOpen(false)}
                  className="w-full px-4 py-2 text-left text-xs text-[#475569] hover:text-[#0F172A] hover:bg-[#F8FAFC] flex items-center gap-2.5 font-medium transition-colors"
                >
                  <SettingsIcon className="w-4 h-4 text-[#64748B]" />
                  Settings
                </button>
              </div>

              <div className="pt-1 border-t border-[#F1F5F9]">
                <button
                  onClick={() => setIsProfileOpen(false)}
                  className="w-full px-4 py-2 text-left text-xs text-[#EF4444] hover:bg-[#FEF2F2] flex items-center gap-2.5 font-semibold transition-colors"
                >
                  <LogOut className="w-4 h-4 text-[#EF4444]" />
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
