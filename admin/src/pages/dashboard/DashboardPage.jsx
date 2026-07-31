import React from 'react';
import {
  Users,
  HardHat,
  ClipboardList,
  BadgeCheck,
  Wrench,
  SearchCheck,
  TrendingUp,
  Activity,
} from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';

export default function DashboardPage() {
  return (
    <PageContainer
      title="KaamSetu Admin Dashboard"
      subtitle="Manage customers, workers, services and platform operations."
      action={
        <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-semibold text-[#0F172A]">
          <Activity className="w-4 h-4 text-[#16A34A] animate-pulse" />
          <span>Realtime System Operational</span>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Top Stat Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <StatCard
            title="Total Customers"
            value="12,450"
            change="+12.5%"
            changeType="positive"
            description="Active accounts"
            icon={Users}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Verified Workers"
            value="1,840"
            change="+8.2%"
            changeType="positive"
            description="Onboarded pros"
            icon={HardHat}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Active Jobs"
            value="342"
            change="Live"
            changeType="positive"
            description="In progress across city"
            icon={ClipboardList}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Pending Verifications"
            value="28"
            change="Action Needed"
            changeType="warning"
            description="KYC documents queued"
            icon={BadgeCheck}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
        </div>

        {/* Platform Core Workflows Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Normal Booking Workflow Card */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-[#EFF6FF] text-[#2563EB]">
                  <Wrench className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-[#0F172A]">
                    Normal Booking Workflow
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Standard price catalog & instant booking
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-[#EFF6FF] text-[#2563EB] text-xs font-bold">
                Catalog Based
              </span>
            </div>
            <p className="text-xs text-[#475569] leading-relaxed">
              Customers select standard tasks (e.g. MCB Replacement, Tap Leakage).
              Market price guide is automatically applied with optional surge percentage options (+30%, +50%).
            </p>
            <div className="pt-2 flex items-center justify-between text-xs text-[#64748B] font-semibold border-t border-[#F1F5F9]">
              <span>Active Catalog Services: 120+</span>
              <span className="text-[#2563EB]">Auto-Matched Pros</span>
            </div>
          </div>

          {/* Inspection Workflow Card */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-[#E0F2FE] text-[#0EA5E9]">
                  <SearchCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-[#0F172A]">
                    Inspection Workflow
                  </h3>
                  <p className="text-xs text-[#64748B]">
                    Home diagnosis & custom quotation approval
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-[#E0F2FE] text-[#0EA5E9] text-xs font-bold">
                Diagnosis Based
              </span>
            </div>
            <p className="text-xs text-[#475569] leading-relaxed">
              Customers pay a visiting charge (₹99) for unknown issues. Verified inspector visits site, uploads diagnosis report, and submits custom quotation subject to Admin market tolerance audit.
            </p>
            <div className="pt-2 flex items-center justify-between text-xs text-[#64748B] font-semibold border-t border-[#F1F5F9]">
              <span>Visiting Charge: ₹99</span>
              <span className="text-[#0EA5E9]">Tolerance Guard On</span>
            </div>
          </div>
        </div>

        {/* Quick System Summary */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-2xl bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A]">
              <TrendingUp className="w-6 h-6 text-[#2563EB]" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-[#0F172A]">
                Platform Architecture Ready
              </h4>
              <p className="text-xs text-[#64748B] mt-0.5">
                Admin dashboard setup (Steps 1–5) complete. Sidebar navigation & shell ready for upcoming modules.
              </p>
            </div>
          </div>
          <span className="px-4 py-2 bg-[#2563EB] text-white text-xs font-bold rounded-xl shadow-xs shrink-0">
            Frontend Shell Configured
          </span>
        </div>
      </div>
    </PageContainer>
  );
}
