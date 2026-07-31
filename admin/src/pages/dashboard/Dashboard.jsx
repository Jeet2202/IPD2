import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  HardHat,
  ClipboardList,
  BadgeCheck,
  RotateCw,
  Calendar,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Briefcase,
  SearchCheck,
  MessageSquareWarning,
  CheckCircle2,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import StatusBadge from '../../components/common/StatusBadge';
import {
  DASHBOARD_STATS,
  WEEKLY_JOB_TRENDS,
  PLATFORM_ACTIVITY,
  PENDING_VERIFICATIONS_SUMMARY,
  RECENT_JOBS,
  ADMIN_ATTENTION_ITEMS,
} from '../../data/dashboardData';

export default function Dashboard() {
  const [dateRange, setDateRange] = useState('Last 7 Days');
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 600);
  };

  return (
    <PageContainer
      title="Dashboard"
      subtitle="Monitor KaamSetu platform activity and operations."
      action={
        <div className="flex items-center gap-3">
          {/* Date Range Selector */}
          <div className="relative">
            <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-semibold text-[#0F172A]">
              <Calendar className="w-4 h-4 text-[#64748B]" />
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="bg-transparent focus:outline-none cursor-pointer pr-1"
              >
                <option value="Today">Today</option>
                <option value="Last 7 Days">Last 7 Days</option>
                <option value="Last 30 Days">Last 30 Days</option>
                <option value="This Month">This Month</option>
              </select>
            </div>
          </div>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            className="p-2 bg-white hover:bg-[#F8FAFC] text-[#64748B] hover:text-[#0F172A] rounded-xl border border-[#E2E8F0] shadow-xs transition-colors"
            title="Refresh Data"
            aria-label="Refresh Dashboard Data"
          >
            <RotateCw
              className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-[#2563EB]' : ''}`}
            />
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* ── Primary Stat Cards ────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <StatCard
            title="Total Customers"
            value={DASHBOARD_STATS.totalCustomers.toLocaleString()}
            change="+12.5%"
            changeType="positive"
            description="vs last month"
            icon={Users}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Verified Workers"
            value={DASHBOARD_STATS.verifiedWorkers.toLocaleString()}
            change="+8.2%"
            changeType="positive"
            description="vs last month"
            icon={HardHat}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Active Jobs"
            value={DASHBOARD_STATS.activeJobs.toLocaleString()}
            change="+15.4%"
            changeType="positive"
            description="vs last week"
            icon={ClipboardList}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Pending Verifications"
            value={DASHBOARD_STATS.pendingVerifications.toLocaleString()}
            change="Action Needed"
            changeType="warning"
            description="Queued documents"
            icon={BadgeCheck}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
        </div>

        {/* ── Secondary Operational Stats ────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[#EFF6FF] text-[#2563EB]">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Today's Jobs</p>
              <p className="text-lg font-black text-[#0F172A]">{DASHBOARD_STATS.todaysJobs}</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[#E0F2FE] text-[#0EA5E9]">
              <SearchCheck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Inspection Requests</p>
              <p className="text-lg font-black text-[#0F172A]">{DASHBOARD_STATS.inspectionRequests}</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[#FEF3C7] text-[#D97706]">
              <MessageSquareWarning className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Pending Complaints</p>
              <p className="text-lg font-black text-[#0F172A]">{DASHBOARD_STATS.pendingComplaints}</p>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-[#DCFCE7] text-[#16A34A]">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-[#64748B]">Completed Today</p>
              <p className="text-lg font-black text-[#0F172A]">{DASHBOARD_STATS.completedJobsToday}</p>
            </div>
          </div>
        </div>

        {/* ── Charts Grid ───────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Job Overview Chart (2 Columns) */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Weekly Job Overview
                </h3>
                <p className="text-xs text-[#64748B]">
                  Normal Jobs vs Inspection Requests
                </p>
              </div>
              <div className="flex items-center gap-2 text-xs font-semibold">
                <span className="inline-flex items-center gap-1 text-[#2563EB]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#2563EB]" /> Normal
                </span>
                <span className="inline-flex items-center gap-1 text-[#0EA5E9] ml-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#0EA5E9]" /> Inspection
                </span>
              </div>
            </div>

            <div className="h-72 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={WEEKLY_JOB_TRENDS} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorNormal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorInspection" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0EA5E9" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#0EA5E9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderColor: '#E2E8F0',
                      borderRadius: '12px',
                      fontSize: '12px',
                      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="normalJobs"
                    name="Normal Jobs"
                    stroke="#2563EB"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#colorNormal)"
                  />
                  <Area
                    type="monotone"
                    dataKey="inspectionRequests"
                    name="Inspection Requests"
                    stroke="#0EA5E9"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#colorInspection)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Platform Activity Bar Chart (1 Column) */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Platform Distribution
              </h3>
              <p className="text-xs text-[#64748B]">
                Breakdown by operational category
              </p>
            </div>

            <div className="h-72 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={PLATFORM_ACTIVITY} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="category" stroke="#94A3B8" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderColor: '#E2E8F0',
                      borderRadius: '12px',
                      fontSize: '12px',
                      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Bar dataKey="count" fill="#2563EB" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ── Tables & Attention Grid ───────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pending Verifications (1 Column) */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Pending Verifications
                </h3>
                <p className="text-xs text-[#64748B]">Worker KYC queued for review</p>
              </div>
              <Link
                to="/admin/verification"
                className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1"
              >
                <span>View All</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-3">
              {PENDING_VERIFICATIONS_SUMMARY.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
                >
                  <div className="space-y-0.5">
                    <p className="text-xs font-bold text-[#0F172A]">{item.worker}</p>
                    <p className="text-[11px] text-[#64748B]">
                      {item.profession} • {item.submitted}
                    </p>
                  </div>
                  <Link
                    to="/admin/verification"
                    className="px-3 py-1 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-lg transition-colors shadow-xs"
                  >
                    Review
                  </Link>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Jobs Table (2 Columns) */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">Recent Jobs</h3>
                <p className="text-xs text-[#64748B]">Latest live platform transactions</p>
              </div>
              <Link
                to="/admin/jobs"
                className="text-xs font-bold text-[#2563EB] hover:underline flex items-center gap-1"
              >
                <span>View All Jobs</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-[#F1F5F9] text-[#94A3B8] font-bold uppercase tracking-wider">
                    <th className="pb-3 px-2">Job ID</th>
                    <th className="pb-3 px-2">Customer</th>
                    <th className="pb-3 px-2">Service</th>
                    <th className="pb-3 px-2">Type</th>
                    <th className="pb-3 px-2">Amount</th>
                    <th className="pb-3 px-2">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                  {RECENT_JOBS.map((job) => (
                    <tr key={job.id} className="hover:bg-[#F8FAFC] transition-colors">
                      <td className="py-3 px-2 font-bold text-[#2563EB]">{job.id}</td>
                      <td className="py-3 px-2 font-semibold">{job.customer}</td>
                      <td className="py-3 px-2 text-[#475569]">{job.service}</td>
                      <td className="py-3 px-2">
                        <span
                          className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                            job.type === 'Inspection'
                              ? 'bg-[#E0F2FE] text-[#0EA5E9]'
                              : 'bg-[#F1F5F9] text-[#475569]'
                          }`}
                        >
                          {job.type}
                        </span>
                      </td>
                      <td className="py-3 px-2 font-bold">{job.amount}</td>
                      <td className="py-3 px-2">
                        <StatusBadge status={job.status} type="job" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* ── Alerts / Needs Attention Card ─────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-[#D97706]" />
            <h3 className="text-base font-extrabold text-[#0F172A]">Needs Attention</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {ADMIN_ATTENTION_ITEMS.map((item) => (
              <div
                key={item.id}
                className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] flex items-center justify-between hover:border-[#CBD5E1] transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      item.type === 'danger'
                        ? 'bg-[#EF4444]'
                        : item.type === 'warning'
                        ? 'bg-[#D97706]'
                        : 'bg-[#2563EB]'
                    }`}
                  />
                  <span className="text-xs font-bold text-[#0F172A]">{item.title}</span>
                </div>
                <Link
                  to={item.link}
                  className="text-xs font-bold text-[#2563EB] hover:underline shrink-0 ml-2"
                >
                  View
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
