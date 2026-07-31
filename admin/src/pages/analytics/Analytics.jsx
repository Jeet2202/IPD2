import React, { useState } from 'react';
import {
  Users,
  HardHat,
  BadgeCheck,
  ClipboardList,
  CheckCircle2,
  SearchCheck,
  IndianRupee,
  Star,
  Calendar,
  RotateCw,
  Download,
  TrendingUp,
  MapPin,
  Wrench,
  AlertTriangle,
  UserCheck,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import { useToast } from '../../components/common/ToastContext';
import {
  ANALYTICS_KPIS,
  CUSTOMER_GROWTH_DATA,
  WORKER_GROWTH_DATA,
  DAILY_BOOKINGS_DATA,
  REVENUE_TREND_DATA,
  SERVICE_CATEGORY_DISTRIBUTION,
  JOBS_BY_CITY,
  WORKER_PERFORMANCE_METRICS,
  CUSTOMER_ANALYTICS_DATA,
  BOOKING_ANALYTICS,
} from '../../data/analytics';

const COLORS = ['#2563EB', '#0EA5E9', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#6366F1'];

export default function Analytics() {
  const { addToast } = useToast();
  const [dateRange, setDateRange] = useState('Last 30 Days');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeWorkerTab, setActiveWorkerTab] = useState('top');
  const [activeCustomerTab, setActiveCustomerTab] = useState('active');

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      addToast({
        title: 'Analytics Refreshed',
        message: 'All performance indicators updated with latest metrics.',
        type: 'success',
      });
    }, 600);
  };

  const handleExport = () => {
    addToast({
      title: 'Export Started',
      message: `Exporting Analytics dataset (${dateRange}) to CSV format.`,
      type: 'info',
    });
  };

  return (
    <PageContainer
      title="Analytics"
      subtitle="Monitor platform growth, operations and business performance."
      action={
        <div className="flex items-center gap-3">
          {/* Date Range Selector */}
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
              <option value="This Quarter">This Quarter</option>
              <option value="Year to Date">Year to Date</option>
            </select>
          </div>

          {/* Export Button */}
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-3 py-2 bg-white hover:bg-[#F8FAFC] text-[#0F172A] rounded-xl border border-[#E2E8F0] shadow-xs text-xs font-bold transition-colors"
          >
            <Download className="w-4 h-4 text-[#64748B]" />
            <span>Export</span>
          </button>

          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            className="p-2 bg-white hover:bg-[#F8FAFC] text-[#64748B] hover:text-[#0F172A] rounded-xl border border-[#E2E8F0] shadow-xs transition-colors"
            title="Refresh Analytics Data"
            aria-label="Refresh Analytics Data"
          >
            <RotateCw
              className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-[#2563EB]' : ''}`}
            />
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* ── TOP KPI CARDS (8 Cards Grid) ─────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Customers"
            value={ANALYTICS_KPIS.totalCustomers.toLocaleString()}
            change={ANALYTICS_KPIS.totalCustomersChange}
            changeType="positive"
            description="vs previous period"
            icon={Users}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Total Workers"
            value={ANALYTICS_KPIS.totalWorkers.toLocaleString()}
            change={ANALYTICS_KPIS.totalWorkersChange}
            changeType="positive"
            description="registered partners"
            icon={HardHat}
            iconBg="bg-[#E0F2FE]"
            iconColor="text-[#0EA5E9]"
          />
          <StatCard
            title="Verified Workers"
            value={ANALYTICS_KPIS.verifiedWorkers.toLocaleString()}
            change={ANALYTICS_KPIS.verifiedWorkersChange}
            changeType="positive"
            description="KYC & badge approved"
            icon={BadgeCheck}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="Active Jobs"
            value={ANALYTICS_KPIS.activeJobs.toLocaleString()}
            change={ANALYTICS_KPIS.activeJobsChange}
            changeType="positive"
            description="currently in progress"
            icon={ClipboardList}
            iconBg="bg-[#ECFDF5]"
            iconColor="text-[#10B981]"
          />
          <StatCard
            title="Completed Jobs"
            value={ANALYTICS_KPIS.completedJobs.toLocaleString()}
            change={ANALYTICS_KPIS.completedJobsChange}
            changeType="positive"
            description="all-time fulfilled"
            icon={CheckCircle2}
            iconBg="bg-[#F0FDF4]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Inspection Requests"
            value={ANALYTICS_KPIS.inspectionRequests.toLocaleString()}
            change={ANALYTICS_KPIS.inspectionRequestsChange}
            changeType="positive"
            description="expert evaluations"
            icon={SearchCheck}
            iconBg="bg-[#F3E8FF]"
            iconColor="text-[#9333EA]"
          />
          <StatCard
            title="Total Revenue"
            value={`₹${(ANALYTICS_KPIS.revenue / 100000).toFixed(2)}L`}
            change={ANALYTICS_KPIS.revenueChange}
            changeType="positive"
            description="gross platform volume"
            icon={IndianRupee}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#15803D]"
          />
          <StatCard
            title="Average Rating"
            value={`${ANALYTICS_KPIS.avgRating} / 5.0`}
            change={ANALYTICS_KPIS.avgRatingChange}
            changeType="positive"
            description="platform-wide score"
            icon={Star}
            iconBg="bg-[#FEF9C3]"
            iconColor="text-[#CA8A04]"
          />
        </div>

        {/* ── CHARTS SECTION 1 ────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Customer Growth Line Chart */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Customer Growth
                </h3>
                <p className="text-xs text-[#64748B]">Cumulative user acquisitions over time</p>
              </div>
              <span className="px-2.5 py-1 bg-[#EFF6FF] text-[#2563EB] text-xs font-bold rounded-lg">
                +14.2% MoM
              </span>
            </div>

            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={CUSTOMER_GROWTH_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
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
                  <Line
                    type="monotone"
                    dataKey="customers"
                    name="Total Customers"
                    stroke="#2563EB"
                    strokeWidth={3}
                    dot={{ fill: '#2563EB', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Worker Growth Line Chart */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Worker Growth & Verification
                </h3>
                <p className="text-xs text-[#64748B]">Registered vs Verified worker onboarding</p>
              </div>
              <div className="flex items-center gap-3 text-xs font-semibold">
                <span className="inline-flex items-center gap-1 text-[#0EA5E9]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#0EA5E9]" /> Total
                </span>
                <span className="inline-flex items-center gap-1 text-[#10B981]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" /> Verified
                </span>
              </div>
            </div>

            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={WORKER_GROWTH_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
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
                  <Line
                    type="monotone"
                    dataKey="total"
                    name="Total Registered"
                    stroke="#0EA5E9"
                    strokeWidth={2.5}
                    dot={{ fill: '#0EA5E9', r: 3 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="verified"
                    name="Verified Workers"
                    stroke="#10B981"
                    strokeWidth={2.5}
                    dot={{ fill: '#10B981', r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ── CHARTS SECTION 2 ────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Revenue Trend Area Chart (2 Cols) */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Revenue Trend
                </h3>
                <p className="text-xs text-[#64748B]">Platform commission fee + inspection revenue split</p>
              </div>
              <div className="flex items-center gap-3 text-xs font-semibold">
                <span className="inline-flex items-center gap-1 text-[#2563EB]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#2563EB]" /> Platform Fee
                </span>
                <span className="inline-flex items-center gap-1 text-[#9333EA]">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#9333EA]" /> Inspection Fee
                </span>
              </div>
            </div>

            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={REVENUE_TREND_DATA} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorPlatform" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563EB" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorInsp" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#9333EA" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#9333EA" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="month" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis
                    stroke="#94A3B8"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => `₹${val / 1000}k`}
                  />
                  <Tooltip
                    formatter={(value) => [`₹${value.toLocaleString()}`, '']}
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
                    dataKey="platformFee"
                    name="Platform Fee"
                    stroke="#2563EB"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#colorPlatform)"
                  />
                  <Area
                    type="monotone"
                    dataKey="inspectionFee"
                    name="Inspection Fee"
                    stroke="#9333EA"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#colorInsp)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Service Category Pie Chart (1 Col) */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Category Distribution
              </h3>
              <p className="text-xs text-[#64748B]">Share of total completed service bookings</p>
            </div>

            <div className="h-56 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={SERVICE_CATEGORY_DISTRIBUTION}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {SERVICE_CATEGORY_DISTRIBUTION.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(val) => [`${val}%`, 'Share']}
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderColor: '#E2E8F0',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-[#F1F5F9]">
              {SERVICE_CATEGORY_DISTRIBUTION.slice(0, 6).map((cat, idx) => (
                <div key={cat.name} className="flex items-center gap-1.5 font-medium text-[#475569]">
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                  />
                  <span className="truncate">{cat.name} ({cat.value}%)</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── CHARTS SECTION 3: DAILY BOOKINGS & JOBS BY CITY ───────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Bookings Bar Chart */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Daily Bookings Breakdown
                </h3>
                <p className="text-xs text-[#64748B]">Normal direct jobs vs Inspection requests per day</p>
              </div>
            </div>

            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={DAILY_BOOKINGS_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderColor: '#E2E8F0',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="normal" name="Normal Jobs" fill="#2563EB" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="inspection" name="Inspection Requests" fill="#0EA5E9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Jobs by City Bar Chart */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Jobs by City Volume
                </h3>
                <p className="text-xs text-[#64748B]">Top active operational cities in Maharashtra</p>
              </div>
            </div>

            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={JOBS_BY_CITY} layout="vertical" margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F1F5F9" />
                  <XAxis type="number" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis dataKey="city" type="category" stroke="#94A3B8" fontSize={11} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      borderColor: '#E2E8F0',
                      borderRadius: '12px',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="jobs" name="Total Jobs" fill="#10B981" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* ── CATEGORY ANALYTICS TABLE ─────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wrench className="w-5 h-5 text-[#2563EB]" />
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Category Analytics Performance
                </h3>
                <p className="text-xs text-[#64748B]">Detailed breakdown per service vertical</p>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#F1F5F9] text-[#94A3B8] font-bold uppercase tracking-wider">
                  <th className="pb-3 px-3">Service Category</th>
                  <th className="pb-3 px-3">Total Jobs</th>
                  <th className="pb-3 px-3">Gross Revenue</th>
                  <th className="pb-3 px-3">Active Workers</th>
                  <th className="pb-3 px-3">Average Rating</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {SERVICE_CATEGORY_DISTRIBUTION.map((cat) => (
                  <tr key={cat.name} className="hover:bg-[#F8FAFC] transition-colors">
                    <td className="py-3 px-3 font-bold text-[#0F172A]">{cat.name}</td>
                    <td className="py-3 px-3">{cat.jobs.toLocaleString()}</td>
                    <td className="py-3 px-3 font-bold text-[#15803D]">₹{cat.revenue.toLocaleString()}</td>
                    <td className="py-3 px-3">{cat.workers}</td>
                    <td className="py-3 px-3">
                      <span className="inline-flex items-center gap-1 font-bold text-[#CA8A04]">
                        <Star className="w-3.5 h-3.5 fill-[#CA8A04]" />
                        {cat.rating}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── CITY ANALYTICS TABLE ─────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-[#0EA5E9]" />
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  City Analytics & Regional Metrics
                </h3>
                <p className="text-xs text-[#64748B]">Key parameters across registered operational cities</p>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#F1F5F9] text-[#94A3B8] font-bold uppercase tracking-wider">
                  <th className="pb-3 px-3">City</th>
                  <th className="pb-3 px-3">Registered Customers</th>
                  <th className="pb-3 px-3">Active Workers</th>
                  <th className="pb-3 px-3">Completed Jobs</th>
                  <th className="pb-3 px-3">City Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {JOBS_BY_CITY.map((city) => (
                  <tr key={city.city} className="hover:bg-[#F8FAFC] transition-colors">
                    <td className="py-3 px-3 font-bold text-[#0F172A]">{city.city}</td>
                    <td className="py-3 px-3">{city.customers.toLocaleString()}</td>
                    <td className="py-3 px-3">{city.workers.toLocaleString()}</td>
                    <td className="py-3 px-3 font-semibold">{city.jobs.toLocaleString()}</td>
                    <td className="py-3 px-3 font-bold text-[#2563EB]">₹{city.revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── WORKER & CUSTOMER ANALYTICS TABS SECTION ───────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Worker Analytics Card */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Worker Performance Analytics
                </h3>
                <p className="text-xs text-[#64748B]">Top performers, lowest ratings & cancellations</p>
              </div>
            </div>

            {/* Sub Tabs */}
            <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-2 text-xs font-semibold">
              <button
                onClick={() => setActiveWorkerTab('top')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeWorkerTab === 'top'
                    ? 'bg-[#2563EB] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Top Workers
              </button>
              <button
                onClick={() => setActiveWorkerTab('lowest')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeWorkerTab === 'lowest'
                    ? 'bg-[#EF4444] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Lowest Rated
              </button>
              <button
                onClick={() => setActiveWorkerTab('active')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeWorkerTab === 'active'
                    ? 'bg-[#0EA5E9] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Most Active
              </button>
              <button
                onClick={() => setActiveWorkerTab('cancellations')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeWorkerTab === 'cancellations'
                    ? 'bg-[#F59E0B] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Cancelled Jobs
              </button>
            </div>

            <div className="space-y-3 pt-1">
              {activeWorkerTab === 'top' &&
                WORKER_PERFORMANCE_METRICS.topWorkers.map((w) => (
                  <div
                    key={w.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
                  >
                    <div>
                      <p className="text-xs font-bold text-[#0F172A]">{w.name} ({w.id})</p>
                      <p className="text-[11px] text-[#64748B]">{w.category} • {w.jobs} completed jobs</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-extrabold text-[#CA8A04] flex items-center justify-end gap-1">
                        <Star className="w-3.5 h-3.5 fill-[#CA8A04]" /> {w.rating}
                      </p>
                      <p className="text-[11px] font-bold text-[#16A34A]">{w.earnings}</p>
                    </div>
                  </div>
                ))}

              {activeWorkerTab === 'lowest' &&
                WORKER_PERFORMANCE_METRICS.lowestRatedWorkers.map((w) => (
                  <div
                    key={w.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[#FEF2F2] border border-[#FCA5A5]"
                  >
                    <div>
                      <p className="text-xs font-bold text-[#991B1B]">{w.name} ({w.id})</p>
                      <p className="text-[11px] text-[#7F1D1D]">{w.category} • {w.warnings} official warnings</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-black text-[#DC2626] flex items-center justify-end gap-1">
                        <Star className="w-3.5 h-3.5 fill-[#DC2626]" /> {w.rating}
                      </p>
                    </div>
                  </div>
                ))}

              {activeWorkerTab === 'active' &&
                WORKER_PERFORMANCE_METRICS.mostActiveWorkers.map((w) => (
                  <div
                    key={w.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
                  >
                    <div>
                      <p className="text-xs font-bold text-[#0F172A]">{w.name} ({w.id})</p>
                      <p className="text-[11px] text-[#64748B]">Active: {w.activeHours}</p>
                    </div>
                    <span className="px-2.5 py-1 bg-[#E0F2FE] text-[#0369A1] text-xs font-bold rounded-lg">
                      {w.completedThisMonth} jobs this month
                    </span>
                  </div>
                ))}

              {activeWorkerTab === 'cancellations' &&
                WORKER_PERFORMANCE_METRICS.mostCancelledJobs.map((w) => (
                  <div
                    key={w.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[#FFFBEB] border border-[#FDE68A]"
                  >
                    <div>
                      <p className="text-xs font-bold text-[#92400E]">{w.name} ({w.id})</p>
                      <p className="text-[11px] text-[#B45309]">Primary reason: {w.reason}</p>
                    </div>
                    <span className="px-2.5 py-1 bg-[#FEE2E2] text-[#991B1B] text-xs font-bold rounded-lg">
                      {w.cancellations} cancellations
                    </span>
                  </div>
                ))}
            </div>
          </div>

          {/* Customer Analytics Card */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Customer Behavior Analytics
                </h3>
                <p className="text-xs text-[#64748B]">Most active, repeat, and inspection power users</p>
              </div>
            </div>

            {/* Sub Tabs */}
            <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-2 text-xs font-semibold">
              <button
                onClick={() => setActiveCustomerTab('active')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeCustomerTab === 'active'
                    ? 'bg-[#2563EB] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Most Active
              </button>
              <button
                onClick={() => setActiveCustomerTab('repeat')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeCustomerTab === 'repeat'
                    ? 'bg-[#10B981] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Repeat Rate
              </button>
              <button
                onClick={() => setActiveCustomerTab('inspections')}
                className={`px-3 py-1.5 rounded-lg transition-colors ${
                  activeCustomerTab === 'inspections'
                    ? 'bg-[#9333EA] text-white font-bold'
                    : 'text-[#64748B] hover:bg-[#F1F5F9]'
                }`}
              >
                Inspection Users
              </button>
            </div>

            <div className="space-y-3 pt-1">
              {activeCustomerTab === 'active' &&
                CUSTOMER_ANALYTICS_DATA.mostActiveCustomers.map((c) => (
                  <div
                    key={c.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]"
                  >
                    <div>
                      <p className="text-xs font-bold text-[#0F172A]">{c.name} ({c.id})</p>
                      <p className="text-[11px] text-[#64748B]">{c.city} • {c.bookings} total bookings</p>
                    </div>
                    <span className="text-xs font-bold text-[#2563EB]">{c.totalSpent}</span>
                  </div>
                ))}

              {activeCustomerTab === 'repeat' && (
                <div className="p-5 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0] space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-[#065F46]">Repeat Customer Volume</span>
                    <span className="text-xl font-black text-[#047857]">
                      {CUSTOMER_ANALYTICS_DATA.repeatCustomersRate}
                    </span>
                  </div>
                  <p className="text-xs text-[#065F46] leading-relaxed">
                    Over {CUSTOMER_ANALYTICS_DATA.repeatCustomersCount.toLocaleString()} customers have booked 2 or more services through KaamSetu.
                  </p>
                </div>
              )}

              {activeCustomerTab === 'inspections' &&
                CUSTOMER_ANALYTICS_DATA.inspectionHeavyCustomers.map((c) => (
                  <div
                    key={c.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-[#F3E8FF] border border-[#E9D5FF]"
                  >
                    <div>
                      <p className="text-xs font-bold text-[#581C87]">{c.name} ({c.id})</p>
                      <p className="text-[11px] text-[#6B21A8]">{c.city} • {c.inspections} requested inspections</p>
                    </div>
                    <span className="px-2.5 py-1 bg-[#9333EA] text-white text-xs font-bold rounded-lg">
                      {c.convertedJobs} converted
                    </span>
                  </div>
                ))}
            </div>
          </div>
        </div>

        {/* ── BOOKING ANALYTICS BREAKDOWN ──────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <h3 className="text-base font-extrabold text-[#0F172A]">
            Booking Pipeline & Completion Metrics
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
              <p className="text-xs text-[#64748B] font-bold">Normal Requests</p>
              <p className="text-lg font-black text-[#0F172A] mt-1">
                {BOOKING_ANALYTICS.normalRequests.toLocaleString()}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#EFF6FF] border border-[#BFDBFE]">
              <p className="text-xs text-[#1E40AF] font-bold">Inspection Requests</p>
              <p className="text-lg font-black text-[#1D4ED8] mt-1">
                {BOOKING_ANALYTICS.inspectionRequests.toLocaleString()}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#ECFDF5] border border-[#A7F3D0]">
              <p className="text-xs text-[#065F46] font-bold">Completed Jobs</p>
              <p className="text-lg font-black text-[#047857] mt-1">
                {BOOKING_ANALYTICS.completed.toLocaleString()}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#FFFBEB] border border-[#FDE68A]">
              <p className="text-xs text-[#92400E] font-bold">Pending Jobs</p>
              <p className="text-lg font-black text-[#B45309] mt-1">
                {BOOKING_ANALYTICS.pending.toLocaleString()}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[#FEF2F2] border border-[#FCA5A5]">
              <p className="text-xs text-[#991B1B] font-bold">Cancelled Jobs</p>
              <p className="text-lg font-black text-[#DC2626] mt-1">
                {BOOKING_ANALYTICS.cancelled.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
