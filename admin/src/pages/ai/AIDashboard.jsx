import React, { useState, useEffect, useCallback } from 'react';
import {
  Sparkles, TrendingUp, Users, HardHat, ClipboardList, IndianRupee,
  Search, BarChart3, Download, RotateCw, AlertTriangle, CheckCircle2,
  Info, Brain, Zap, Activity
} from 'lucide-react';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts';
import { aiAnalytics } from '../../services/aiService';
import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import { CardSkeleton, ChartSkeleton } from '../../components/common/SkeletonLoader';
import { useToast } from '../../components/common/ToastContext';

const TABS = [
  { id: 'overview', label: 'Overview', icon: Activity },
  { id: 'bookings', label: 'Bookings', icon: ClipboardList },
  { id: 'workers', label: 'Workers', icon: HardHat },
  { id: 'services', label: 'Services & Search', icon: Search },
  { id: 'pricing', label: 'Pricing', icon: IndianRupee },
];

const CHART_COLORS = ['#6366F1', '#2563EB', '#10B981', '#F59E0B', '#3B82F6', '#8B5CF6'];

function InsightCard({ insight }) {
  const config = {
    positive: { bg: 'bg-[#D1FAE5]', border: 'border-[#6EE7B7]', text: 'text-[#065F46]', icon: CheckCircle2, iconColor: 'text-[#059669]' },
    negative: { bg: 'bg-[#FEE2E2]', border: 'border-[#FCA5A5]', text: 'text-[#7F1D1D]', icon: AlertTriangle, iconColor: 'text-[#EF4444]' },
    neutral:  { bg: 'bg-[#EFF6FF]', border: 'border-[#BFDBFE]', text: 'text-[#1E3A5F]', icon: Info, iconColor: 'text-[#2563EB]' },
  }[insight.sentiment] || {};
  const Icon = config.icon;

  return (
    <div className={`flex items-start gap-3 p-4 rounded-2xl border ${config.bg} ${config.border}`}>
      <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${config.iconColor}`} />
      <div>
        <p className={`text-xs font-semibold ${config.text}`}>{insight.insight}</p>
        <p className="text-[10px] text-[#64748B] mt-0.5 capitalize font-medium">{insight.metric_type}</p>
      </div>
    </div>
  );
}

function useAIData(fetcher) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetcher();
      setData(res);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);
  return { data, loading, error, reload: load };
}

// ─── TAB: Overview ────────────────────────────────────────────────────────────
function OverviewTab() {
  const { data: stats, loading: statsLoading } = useAIData(aiAnalytics.dashboard);
  const { data: insights, loading: insightsLoading } = useAIData(aiAnalytics.insights);

  if (statsLoading) return <div className="space-y-4"><CardSkeleton count={4} /><ChartSkeleton /></div>;

  if (!stats) return (
    <div className="bg-[#FEF2F2] border border-[#FECACA] rounded-2xl p-6 text-center text-[#991B1B] text-sm font-medium">
      Could not load dashboard stats. Ensure the AI microservice is running.
    </div>
  );

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Today's Bookings" value={stats.today_bookings} icon={ClipboardList} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" description="Live count" />
        <StatCard title="Today's Revenue" value={`₹${stats.today_revenue?.toLocaleString('en-IN') || 0}`} icon={IndianRupee} iconBg="bg-[#D1FAE5]" iconColor="text-[#059669]" description="Completed bookings" />
        <StatCard title="Online Workers" value={stats.online_workers} icon={HardHat} iconBg="bg-[#F5F3FF]" iconColor="text-[#7C3AED]" description={`${stats.active_workers} total active`} />
        <StatCard title="Avg. Rating" value={`${stats.average_rating} ★`} icon={Sparkles} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" description="Platform-wide" />
      </div>

      {/* Secondary stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Completed Jobs" value={stats.completed_jobs} icon={CheckCircle2} iconBg="bg-[#D1FAE5]" iconColor="text-[#059669]" />
        <StatCard title="Pending Jobs" value={stats.pending_jobs} icon={Activity} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
        <StatCard title="Top Service" value={stats.top_service} icon={Zap} iconBg="bg-[#F5F3FF]" iconColor="text-[#7C3AED]" />
        <StatCard title="Avg. Quote" value={`₹${stats.average_price?.toLocaleString('en-IN') || 0}`} icon={IndianRupee} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
      </div>

      {/* Insights */}
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-[#7C3AED]" />
          <h3 className="text-sm font-bold text-[#0F172A]">AI-Generated Business Insights</h3>
          <span className="text-[10px] font-bold text-[#7C3AED] bg-[#F5F3FF] px-2 py-0.5 rounded-full">Rule-Based</span>
        </div>
        {insightsLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map(i => <div key={i} className="h-12 bg-[#F1F5F9] rounded-xl animate-pulse" />)}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {(insights || []).map((ins, i) => <InsightCard key={i} insight={ins} />)}
            {(!insights || insights.length === 0) && (
              <p className="text-xs text-[#94A3B8] col-span-2 text-center py-4">No insights available yet.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── TAB: Bookings ────────────────────────────────────────────────────────────
function BookingsTab() {
  const { data, loading, error } = useAIData(aiAnalytics.bookings);

  if (loading) return <div className="space-y-4"><CardSkeleton count={4} /><ChartSkeleton /></div>;
  if (error || !data) return <div className="text-center py-10 text-xs text-[#94A3B8]">Could not load booking analytics.</div>;

  const statusData = [
    { name: 'Completed', value: data.completed_bookings },
    { name: 'Pending', value: data.pending_bookings },
    { name: 'Active', value: data.active_bookings },
    { name: 'Cancelled', value: data.cancelled_bookings },
  ];

  const trendLabels = data.bookings_trend?.labels || [];
  const trendValues = data.bookings_trend?.datasets?.[0]?.data || [];
  const chartData = trendLabels.map((label, i) => ({ date: label, bookings: trendValues[i] || 0 }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Bookings" value={data.total_bookings} icon={ClipboardList} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
        <StatCard title="Completed" value={data.completed_bookings} icon={CheckCircle2} iconBg="bg-[#D1FAE5]" iconColor="text-[#059669]" />
        <StatCard title="Pending" value={data.pending_bookings} icon={Activity} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
        <StatCard title="Avg. Completion" value={`${data.average_completion_time_hours}h`} icon={Zap} iconBg="bg-[#F5F3FF]" iconColor="text-[#7C3AED]" description="Average time" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Trend Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-[#E2E8F0] p-5">
          <h3 className="text-sm font-bold text-[#0F172A] mb-4">Booking Trend (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorBookings" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7C3AED" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#7C3AED" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#94A3B8' }} />
              <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} />
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 11 }} />
              <Area type="monotone" dataKey="bookings" stroke="#7C3AED" fill="url(#colorBookings)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Status Pie */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
          <h3 className="text-sm font-bold text-[#0F172A] mb-4">Status Breakdown</h3>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} paddingAngle={3}>
                {statusData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-x-4 gap-y-1 justify-center mt-2">
            {statusData.map((s, i) => (
              <div key={i} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[i] }} />
                <span className="text-[9px] text-[#64748B] font-medium">{s.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── TAB: Workers ─────────────────────────────────────────────────────────────
function WorkersTab() {
  const { data, loading } = useAIData(aiAnalytics.workers);
  if (loading) return <div className="space-y-4"><CardSkeleton count={4} /><ChartSkeleton /></div>;
  if (!data) return <div className="text-center py-10 text-xs text-[#94A3B8]">Could not load worker analytics.</div>;

  const statusLabels = data.status_distribution?.labels || [];
  const statusValues = data.status_distribution?.datasets?.[0]?.data || [];
  const statusData = statusLabels.map((l, i) => ({ name: l, value: statusValues[i] || 0 }));

  const perfData = [
    { name: 'Completion Rate', value: data.completion_rate },
    { name: 'Acceptance Rate', value: data.acceptance_rate },
    { name: 'Cancellation Rate', value: data.cancellation_rate },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Workers" value={data.total_workers} icon={HardHat} iconBg="bg-[#F5F3FF]" iconColor="text-[#7C3AED]" />
        <StatCard title="Verified" value={data.verified_workers} icon={CheckCircle2} iconBg="bg-[#D1FAE5]" iconColor="text-[#059669]" />
        <StatCard title="Available Now" value={data.available_workers} icon={Zap} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
        <StatCard title="Avg. Rating" value={`${data.average_rating} ★`} icon={Sparkles} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
          <h3 className="text-sm font-bold text-[#0F172A] mb-4">Worker Status Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#94A3B8' }} />
              <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} />
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 11 }} />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {statusData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
          <h3 className="text-sm font-bold text-[#0F172A] mb-4">Performance Rates (%)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={perfData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis type="number" tick={{ fontSize: 9, fill: '#94A3B8' }} domain={[0, 100]} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 9, fill: '#64748B' }} width={110} />
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 11 }} />
              <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                {perfData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// ─── TAB: Services & Search ───────────────────────────────────────────────────
function ServicesSearchTab() {
  const { data: services, loading: sLoading } = useAIData(aiAnalytics.services);
  const { data: search, loading: qLoading } = useAIData(aiAnalytics.search);

  if (sLoading || qLoading) return <div className="space-y-4"><ChartSkeleton /><ChartSkeleton /></div>;

  const catLabels = services?.category_distribution?.labels || [];
  const catValues = services?.category_distribution?.datasets?.[0]?.data || [];
  const catData = catLabels.map((l, i) => ({ name: l, count: catValues[i] || 0 }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Category Distribution */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
          <h3 className="text-sm font-bold text-[#0F172A] mb-4">Category Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={catData} dataKey="count" nameKey="name" cx="50%" cy="50%" outerRadius={80} paddingAngle={3}>
                {catData.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Most Requested Services */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
          <h3 className="text-sm font-bold text-[#0F172A] mb-4">Most Requested Services</h3>
          <div className="space-y-2">
            {(services?.most_requested_services || []).map((s, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-[10px] font-black text-[#94A3B8] w-5 text-right">{i + 1}</span>
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-[11px] font-semibold text-[#0F172A]">{s.service_name || s.name}</span>
                    <span className="text-[10px] font-bold text-[#7C3AED]">{s.request_count || s.count}</span>
                  </div>
                  <div className="h-1.5 bg-[#F1F5F9] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.min(100, ((s.request_count || s.count || 0) / ((services?.most_requested_services?.[0]?.request_count || 1))) * 100)}%`,
                        backgroundColor: CHART_COLORS[i % CHART_COLORS.length]
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
            {(!services?.most_requested_services || services.most_requested_services.length === 0) && (
              <p className="text-xs text-[#94A3B8] text-center py-4">No service data yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Search Analytics */}
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-[#0F172A]">AI Search Analytics</h3>
          <div className="flex items-center gap-4 text-xs text-[#64748B]">
            <span>Total: <span className="font-bold text-[#0F172A]">{search?.total_searches || 0}</span></span>
            <span>Success Rate: <span className="font-bold text-[#059669]">{search?.success_rate || 0}%</span></span>
          </div>
        </div>
        <div>
          <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider mb-2">Trending Queries</p>
          <div className="flex flex-wrap gap-2">
            {(search?.trending_searches || []).map((q, i) => (
              <span key={i} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#F5F3FF] text-[#7C3AED] text-[11px] font-semibold">
                <TrendingUp className="w-3 h-3" />
                {q}
              </span>
            ))}
            {(!search?.trending_searches || search.trending_searches.length === 0) && (
              <p className="text-xs text-[#94A3B8]">No trending searches yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── TAB: Pricing ─────────────────────────────────────────────────────────────
function PricingTab() {
  const { data, loading } = useAIData(aiAnalytics.pricing);
  if (loading) return <div className="space-y-4"><CardSkeleton count={4} /><ChartSkeleton /></div>;
  if (!data) return <div className="text-center py-10 text-xs text-[#94A3B8]">Could not load pricing analytics.</div>;

  const distLabels = data.price_distribution?.labels || [];
  const distValues = data.price_distribution?.datasets?.[0]?.data || [];
  const distData = distLabels.map((l, i) => ({ range: String(l).slice(0, 12), count: distValues[i] || 0 }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Avg. Quote" value={`₹${data.average_quote?.toLocaleString('en-IN') || 0}`} icon={IndianRupee} iconBg="bg-[#EFF6FF]" iconColor="text-[#2563EB]" />
        <StatCard title="Min Quote" value={`₹${data.minimum_quote?.toLocaleString('en-IN') || 0}`} icon={IndianRupee} iconBg="bg-[#D1FAE5]" iconColor="text-[#059669]" />
        <StatCard title="Max Quote" value={`₹${data.maximum_quote?.toLocaleString('en-IN') || 0}`} icon={IndianRupee} iconBg="bg-[#FEE2E2]" iconColor="text-[#EF4444]" />
        <StatCard title="Std. Deviation" value={`₹${data.price_variance?.toFixed(0) || 0}`} icon={Activity} iconBg="bg-[#FEF3C7]" iconColor="text-[#D97706]" description="Price variance" />
      </div>

      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5">
        <h3 className="text-sm font-bold text-[#0F172A] mb-4">Quote Price Distribution</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={distData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="range" tick={{ fontSize: 9, fill: '#94A3B8' }} />
            <YAxis tick={{ fontSize: 9, fill: '#94A3B8' }} />
            <Tooltip contentStyle={{ borderRadius: 12, border: '1px solid #E2E8F0', fontSize: 11 }} />
            <Bar dataKey="count" fill="#7C3AED" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function AIDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [isExporting, setIsExporting] = useState(false);
  const { addToast } = useToast();

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const res = await aiAnalytics.exportDataset('bookings', 'csv');
      addToast({ title: 'Export Complete', message: `${res.record_count} records exported successfully.`, type: 'success' });
    } catch {
      addToast({ title: 'Export Failed', message: 'Could not reach AI service. Please try again.', type: 'error' });
    } finally {
      setIsExporting(false);
    }
  };

  const TabContent = {
    overview: OverviewTab,
    bookings: BookingsTab,
    workers: WorkersTab,
    services: ServicesSearchTab,
    pricing: PricingTab,
  }[activeTab];

  return (
    <PageContainer
      title="AI Intelligence Hub"
      subtitle="Live analytics and business intelligence powered by the KaamSetu AI Platform."
      action={
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#F5F3FF] text-[#7C3AED] text-[10px] font-bold">
            <Brain className="w-3.5 h-3.5" />
            Phase 5.6 Live
          </div>
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#7C3AED] text-white text-xs font-bold hover:bg-[#6D28D9] disabled:opacity-60 transition-all"
          >
            {isExporting ? <RotateCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            Export Dataset
          </button>
        </div>
      }
    >
      {/* Tab bar */}
      <div className="flex gap-1 bg-[#F8FAFC] border border-[#E2E8F0] rounded-2xl p-1 mb-6 overflow-x-auto">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
              activeTab === id
                ? 'bg-white text-[#7C3AED] shadow-sm border border-[#E2E8F0]'
                : 'text-[#64748B] hover:text-[#0F172A] hover:bg-white/60'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <TabContent />
    </PageContainer>
  );
}
