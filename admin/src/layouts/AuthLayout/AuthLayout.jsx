import React from 'react';
import { Outlet } from 'react-router-dom';

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center p-4 antialiased">
      <div className="w-full max-w-md">
        <Outlet />
      </div>
      <footer className="mt-8 text-center text-xs text-[#94A3B8] font-medium">
        &copy; {new Date().getFullYear()} KaamSetu Technologies Inc. All rights reserved.
      </footer>
    </div>
  );
}
