import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Wrench, Mail, Lock, Eye, EyeOff, ShieldCheck, ArrowRight } from 'lucide-react';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('admin@kaamsetu.com');
  const [password, setPassword] = useState('admin123');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!email.trim()) {
      errs.email = 'Email address is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errs.email = 'Please enter a valid email address';
    }
    if (!password) {
      errs.password = 'Password is required';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      // Demo navigation to admin dashboard
      navigate('/admin/dashboard');
    }
  };

  return (
    <div className="space-y-6">
      {/* Brand Header */}
      <div className="text-center space-y-2">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#0EA5E9] text-white flex items-center justify-center mx-auto shadow-lg shadow-[#2563EB]/25">
          <Wrench className="w-7 h-7" />
        </div>
        <h1 className="text-2xl font-black text-[#0F172A] tracking-tight">
          Welcome to KaamSetu Admin
        </h1>
        <p className="text-xs text-[#64748B] font-medium">
          Sign in to manage platform operations
        </p>
      </div>

      {/* Main Login Card */}
      <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 sm:p-8 shadow-xl space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Input */}
          <div className="space-y-1">
            <label className="block text-xs font-bold text-[#0F172A]">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@kaamsetu.com"
                className={`w-full pl-10 pr-4 py-2.5 bg-[#F8FAFC] border rounded-xl text-xs text-[#0F172A] font-medium placeholder-[#94A3B8] focus:outline-none focus:ring-2 transition-all ${
                  errors.email
                    ? 'border-[#EF4444] focus:ring-[#EF4444]/20'
                    : 'border-[#E2E8F0] focus:ring-[#2563EB]/20 focus:border-[#2563EB]'
                }`}
              />
            </div>
            {errors.email && (
              <p className="text-[11px] font-bold text-[#EF4444] mt-1">
                {errors.email}
              </p>
            )}
          </div>

          {/* Password Input */}
          <div className="space-y-1">
            <label className="block text-xs font-bold text-[#0F172A]">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8]" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className={`w-full pl-10 pr-10 py-2.5 bg-[#F8FAFC] border rounded-xl text-xs text-[#0F172A] font-medium placeholder-[#94A3B8] focus:outline-none focus:ring-2 transition-all ${
                  errors.password
                    ? 'border-[#EF4444] focus:ring-[#EF4444]/20'
                    : 'border-[#E2E8F0] focus:ring-[#2563EB]/20 focus:border-[#2563EB]'
                }`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#0F172A]"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-[11px] font-bold text-[#EF4444] mt-1">
                {errors.password}
              </p>
            )}
          </div>

          {/* Remember & Forgot Options */}
          <div className="flex items-center justify-between text-xs pt-1">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-[#E2E8F0] text-[#2563EB] focus:ring-[#2563EB]/20"
              />
              <span className="font-semibold text-[#64748B]">Remember Me</span>
            </label>
            <a
              href="#forgot"
              onClick={(e) => {
                e.preventDefault();
                alert('Contact system administrator for password resets.');
              }}
              className="font-bold text-[#2563EB] hover:underline"
            >
              Forgot Password?
            </a>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-3 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-extrabold text-xs rounded-xl shadow-md shadow-[#2563EB]/30 transition-all flex items-center justify-center gap-2"
          >
            <span>Sign In to Admin Panel</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Security Info Badge */}
        <div className="p-3 bg-[#EFF6FF] rounded-2xl border border-[#BFDBFE] flex items-center gap-3">
          <ShieldCheck className="w-5 h-5 text-[#2563EB] shrink-0" />
          <div className="text-[11px]">
            <p className="font-extrabold text-[#1E40AF]">Secure Admin Access</p>
            <p className="text-[#3B82F6]">Authorized personnel only</p>
          </div>
        </div>
      </div>
    </div>
  );
}
