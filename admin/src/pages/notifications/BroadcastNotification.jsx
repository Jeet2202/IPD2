import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Megaphone,
  Users,
  Send,
  Calendar,
  Clock,
  Smartphone,
  Image as ImageIcon,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ArrowLeft,
  X,
  Filter,
} from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';
import ConfirmModal from '../../components/common/ConfirmModal';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import { useToast } from '../../components/common/ToastContext';
import { BROADCASTS_DATA } from '../../data/broadcasts';

export default function BroadcastNotification() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [recentBroadcasts, setRecentBroadcasts] = useState(BROADCASTS_DATA);

  // Form State
  const [audienceType, setAudienceType] = useState('All Users'); // All Users | All Customers | All Workers | Verified Workers | Unverified Workers | Custom Segment
  const [customSegment, setCustomSegment] = useState({
    city: 'All',
    profession: 'All',
    category: 'All',
    accountStatus: 'Active',
    verificationStatus: 'Verified',
  });

  const [notificationType, setNotificationType] = useState('General'); // General | Service Update | Promotion | Safety Alert | Maintenance | Payment Update | Policy Update | Urgent Alert

  const [title, setTitle] = useState('');
  const [shortMessage, setShortMessage] = useState('');
  const [detailedMessage, setDetailedMessage] = useState('');
  const [actionLabel, setActionLabel] = useState('View Details');
  const [actionRoute, setActionRoute] = useState('/home');
  const [bannerUrl, setBannerUrl] = useState('');

  const [scheduleType, setScheduleType] = useState('Now'); // Now | Scheduled
  const [scheduleDate, setScheduleDate] = useState('2026-04-01');
  const [scheduleTime, setScheduleTime] = useState('10:00');

  // Preview App View Tab
  const [previewTab, setPreviewTab] = useState('Customer'); // Customer | Worker

  // Send Confirmation Modal
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);

  // Live Dynamic Audience Estimate
  const estimatedRecipients = useMemo(() => {
    if (audienceType === 'All Users') return 65400;
    if (audienceType === 'All Customers') return 48920;
    if (audienceType === 'All Workers') return 16480;
    if (audienceType === 'Verified Workers') return 14200;
    if (audienceType === 'Unverified Workers') return 2280;
    if (audienceType === 'Custom Segment') {
      let base = 12480;
      if (customSegment.city === 'Mumbai') base = 4800;
      if (customSegment.city === 'Bengaluru') base = 5600;
      if (customSegment.profession === 'Electrician') base = 2100;
      if (customSegment.profession === 'Plumber') base = 1800;
      return base;
    }
    return 10000;
  }, [audienceType, customSegment]);

  const handleOpenConfirm = (e) => {
    e.preventDefault();
    if (!title.trim() || !shortMessage.trim()) {
      addToast({
        title: 'Missing Required Fields',
        message: 'Notification title and short message are required.',
        type: 'error',
      });
      return;
    }
    setConfirmModalOpen(true);
  };

  const handleSendBroadcast = () => {
    const newBroadcast = {
      id: 'BRD-' + Math.floor(100 + Math.random() * 900),
      title: title.trim(),
      shortMessage: shortMessage.trim(),
      detailedMessage: detailedMessage.trim(),
      notificationType,
      audienceType,
      audienceFilters: audienceType === 'Custom Segment' ? customSegment : {},
      actionLabel: actionLabel.trim(),
      actionRoute: actionRoute.trim(),
      scheduleType,
      scheduledAt:
        scheduleType === 'Now'
          ? 'Just now'
          : `${scheduleDate} ${scheduleTime} (IST)`,
      estimatedRecipients,
      status: scheduleType === 'Now' ? 'Sent' : 'Scheduled',
      bannerImage: bannerUrl.trim() || null,
      createdAt: 'Just now',
    };

    setRecentBroadcasts((prev) => [newBroadcast, ...prev]);

    addToast({
      title: scheduleType === 'Now' ? 'Broadcast Dispatched!' : 'Broadcast Scheduled!',
      message: `Announcement broadcast set for ~${estimatedRecipients.toLocaleString()} users. (Frontend demo execution)`,
      type: 'success',
    });

    setConfirmModalOpen(false);

    // Reset Form
    setTitle('');
    setShortMessage('');
    setDetailedMessage('');
    setBannerUrl('');
  };

  return (
    <PageContainer
      title={
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/admin/notifications')}
            className="p-1.5 rounded-xl bg-white border border-[#E2E8F0] text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <span>Broadcast Notification</span>
        </div>
      }
      subtitle="Create and schedule push announcements for KaamSetu customers and professionals."
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT COLUMN — FORM BUILDER (2 COLS) */}
        <div className="lg:col-span-2 space-y-6">
          <form onSubmit={handleOpenConfirm} className="space-y-6">
            {/* 1. AUDIENCE SELECTION */}
            <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
              <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
                <h3 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider flex items-center gap-1.5">
                  <Users className="w-4 h-4 text-[#2563EB]" />
                  1. Target Audience
                </h3>
                <span className="text-xs font-bold text-[#2563EB] bg-[#EFF6FF] px-2.5 py-0.5 rounded-full border border-[#BFDBFE]">
                  Estimated: ~{estimatedRecipients.toLocaleString()} users (Demo)
                </span>
              </div>

              {/* Radio Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { id: 'All Users', label: 'All Users (Customers & Workers)' },
                  { id: 'All Customers', label: 'All Customers Only' },
                  { id: 'All Workers', label: 'All Workers Only' },
                  { id: 'Verified Workers', label: 'Verified Workers Only' },
                  { id: 'Unverified Workers', label: 'Unverified Workers' },
                  { id: 'Custom Segment', label: 'Custom Filter Segment' },
                ].map((aud) => (
                  <label
                    key={aud.id}
                    className={`p-3 rounded-xl border cursor-pointer transition-all space-y-1 ${
                      audienceType === aud.id
                        ? 'bg-[#EFF6FF] border-[#2563EB] ring-2 ring-[#2563EB]/20 text-[#2563EB]'
                        : 'bg-[#F8FAFC] border-[#E2E8F0] text-[#334155] hover:bg-[#F1F5F9]'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="audienceType"
                        checked={audienceType === aud.id}
                        onChange={() => setAudienceType(aud.id)}
                        className="w-3.5 h-3.5 text-[#2563EB]"
                      />
                      <span className="text-xs font-bold">{aud.label}</span>
                    </div>
                  </label>
                ))}
              </div>

              {/* CUSTOM SEGMENT FILTERS IF SELECTED */}
              {audienceType === 'Custom Segment' && (
                <div className="pt-3 border-t border-[#F1F5F9] space-y-3 bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0]">
                  <span className="text-xs font-bold text-[#0F172A] flex items-center gap-1">
                    <Filter className="w-3.5 h-3.5 text-[#2563EB]" />
                    Custom Segment Criteria
                  </span>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-bold text-[#64748B] mb-1">
                        Target City
                      </label>
                      <select
                        value={customSegment.city}
                        onChange={(e) =>
                          setCustomSegment((prev) => ({ ...prev, city: e.target.value }))
                        }
                        className="w-full p-2 bg-white border border-[#E2E8F0] rounded-lg font-medium"
                      >
                        <option value="All">All Cities</option>
                        <option value="Mumbai">Mumbai</option>
                        <option value="Bengaluru">Bengaluru</option>
                        <option value="Delhi NCR">Delhi NCR</option>
                        <option value="Pune">Pune</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#64748B] mb-1">
                        Profession
                      </label>
                      <select
                        value={customSegment.profession}
                        onChange={(e) =>
                          setCustomSegment((prev) => ({ ...prev, profession: e.target.value }))
                        }
                        className="w-full p-2 bg-white border border-[#E2E8F0] rounded-lg font-medium"
                      >
                        <option value="All">All Professions</option>
                        <option value="Electrician">Electrician</option>
                        <option value="Plumber">Plumber</option>
                        <option value="AC Specialist">AC Specialist</option>
                        <option value="Carpenter">Carpenter</option>
                        <option value="Painter">Painter</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-bold text-[#64748B] mb-1">
                        Verification Status
                      </label>
                      <select
                        value={customSegment.verificationStatus}
                        onChange={(e) =>
                          setCustomSegment((prev) => ({
                            ...prev,
                            verificationStatus: e.target.value,
                          }))
                        }
                        className="w-full p-2 bg-white border border-[#E2E8F0] rounded-lg font-medium"
                      >
                        <option value="Verified">Verified Only</option>
                        <option value="Pending">Pending Only</option>
                        <option value="Rejected">Rejected</option>
                        <option value="All">All</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 2. NOTIFICATION TYPE & CONTENT */}
            <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
              <h3 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider flex items-center gap-1.5 border-b border-[#F1F5F9] pb-3">
                <Megaphone className="w-4 h-4 text-[#2563EB]" />
                2. Notification Content & Type
              </h3>

              {/* Notification Type Selector */}
              <div>
                <label className="block text-xs font-bold text-[#0F172A] mb-1">
                  Announcement Category / Type
                </label>
                <select
                  value={notificationType}
                  onChange={(e) => setNotificationType(e.target.value)}
                  className="w-full p-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
                >
                  <option value="General">General Announcement</option>
                  <option value="Service Update">Service Update</option>
                  <option value="Promotion">Promotion & Discount</option>
                  <option value="Safety Alert">Safety & Security Alert</option>
                  <option value="Maintenance">Scheduled Maintenance</option>
                  <option value="Payment Update">Payment & Payout Update</option>
                  <option value="Policy Update">Policy Update</option>
                  <option value="Urgent Alert">Urgent Critical Alert</option>
                </select>
              </div>

              {/* Title Input with live character count */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-bold text-[#0F172A]">
                    Notification Title <span className="text-[#DC2626]">*</span>
                  </label>
                  <span
                    className={`text-[10px] font-bold ${
                      title.length > 60 ? 'text-[#DC2626]' : 'text-[#64748B]'
                    }`}
                  >
                    {title.length} / 60
                  </span>
                </div>
                <input
                  type="text"
                  maxLength={60}
                  placeholder="e.g., Safety Reminder: Verify Professional Badge ID"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full p-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              {/* Short Message Input with live character count */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-bold text-[#0F172A]">
                    Short Push Message <span className="text-[#DC2626]">*</span>
                  </label>
                  <span
                    className={`text-[10px] font-bold ${
                      shortMessage.length > 160 ? 'text-[#DC2626]' : 'text-[#64748B]'
                    }`}
                  >
                    {shortMessage.length} / 160
                  </span>
                </div>
                <textarea
                  rows={2}
                  maxLength={160}
                  placeholder="Brief message displayed on phone lock screen / banner notification..."
                  value={shortMessage}
                  onChange={(e) => setShortMessage(e.target.value)}
                  className="w-full p-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              {/* Optional Detailed Message */}
              <div>
                <label className="block text-xs font-bold text-[#0F172A] mb-1">
                  Optional Detailed Announcement Text (App Modal View)
                </label>
                <textarea
                  rows={3}
                  placeholder="Full announcement body shown when customer/worker taps notification..."
                  value={detailedMessage}
                  onChange={(e) => setDetailedMessage(e.target.value)}
                  className="w-full p-3 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
              </div>

              {/* Action Button & Link */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#0F172A] mb-1">
                    Action Button Label
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., View Details / Book Now"
                    value={actionLabel}
                    onChange={(e) => setActionLabel(e.target.value)}
                    className="w-full p-2.5 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#0F172A] mb-1">
                    Action Target Route / Link
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., /services/ac-repair or /help/safety"
                    value={actionRoute}
                    onChange={(e) => setActionRoute(e.target.value)}
                    className="w-full p-2.5 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
                  />
                </div>
              </div>

              {/* Optional Image Banner Upload Placeholder */}
              <div>
                <label className="block text-xs font-bold text-[#0F172A] mb-1">
                  Banner Image URL (Optional Demo Placeholder)
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="https://images.unsplash.com/... or paste image link"
                    value={bannerUrl}
                    onChange={(e) => setBannerUrl(e.target.value)}
                    className="flex-1 p-2.5 text-xs bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
                  />
                  {bannerUrl && (
                    <button
                      type="button"
                      onClick={() => setBannerUrl('')}
                      className="px-3 py-2 text-xs font-bold text-[#DC2626] bg-[#FEE2E2] rounded-xl"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* 3. SCHEDULE OPTIONS & SUBMIT */}
            <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
              <h3 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider flex items-center gap-1.5 border-b border-[#F1F5F9] pb-3">
                <Clock className="w-4 h-4 text-[#2563EB]" />
                3. Dispatch Schedule
              </h3>

              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 text-xs font-bold cursor-pointer">
                  <input
                    type="radio"
                    name="scheduleType"
                    checked={scheduleType === 'Now'}
                    onChange={() => setScheduleType('Now')}
                    className="w-4 h-4 text-[#2563EB]"
                  />
                  <span>Send Immediately (Now)</span>
                </label>

                <label className="flex items-center gap-2 text-xs font-bold cursor-pointer">
                  <input
                    type="radio"
                    name="scheduleType"
                    checked={scheduleType === 'Scheduled'}
                    onChange={() => setScheduleType('Scheduled')}
                    className="w-4 h-4 text-[#2563EB]"
                  />
                  <span>Schedule for Later</span>
                </label>
              </div>

              {scheduleType === 'Scheduled' && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
                  <div>
                    <label className="block text-[11px] font-bold text-[#64748B] mb-1">
                      Date
                    </label>
                    <input
                      type="date"
                      value={scheduleDate}
                      onChange={(e) => setScheduleDate(e.target.value)}
                      className="w-full p-2 text-xs bg-white border border-[#E2E8F0] rounded-lg font-semibold"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-[#64748B] mb-1">
                      Time
                    </label>
                    <input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => setScheduleTime(e.target.value)}
                      className="w-full p-2 text-xs bg-white border border-[#E2E8F0] rounded-lg font-semibold"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-[#64748B] mb-1">
                      Timezone
                    </label>
                    <div className="p-2 text-xs bg-[#E2E8F0]/60 rounded-lg font-bold text-[#334155]">
                      India Standard Time (IST)
                    </div>
                  </div>
                </div>
              )}

              {/* Action Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  className="w-full py-3 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-extrabold rounded-xl shadow-md transition-all flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {scheduleType === 'Now'
                    ? 'Send Broadcast Notification'
                    : 'Schedule Broadcast Announcement'}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* RIGHT COLUMN — LIVE PREVIEW & RECENT BROADCASTS (1 COL) */}
        <div className="space-y-6">
          {/* MOBILE PUSH NOTIFICATION PREVIEW */}
          <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <h3 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider flex items-center gap-1.5">
                <Smartphone className="w-4 h-4 text-[#2563EB]" />
                Live Mobile Lockscreen Preview
              </h3>
            </div>

            {/* App Preview Tabs */}
            <div className="flex bg-[#F1F5F9] p-1 rounded-xl gap-1">
              <button
                type="button"
                onClick={() => setPreviewTab('Customer')}
                className={`flex-1 py-1.5 text-[11px] font-bold rounded-lg transition-all ${
                  previewTab === 'Customer'
                    ? 'bg-white text-[#2563EB] shadow-2xs'
                    : 'text-[#64748B]'
                }`}
              >
                Customer App
              </button>
              <button
                type="button"
                onClick={() => setPreviewTab('Worker')}
                className={`flex-1 py-1.5 text-[11px] font-bold rounded-lg transition-all ${
                  previewTab === 'Worker'
                    ? 'bg-white text-[#2563EB] shadow-2xs'
                    : 'text-[#64748B]'
                }`}
              >
                Worker App
              </button>
            </div>

            {/* Phone Card Mockup Container */}
            <div className="bg-[#0F172A] p-4 rounded-3xl border-4 border-[#334155] shadow-xl space-y-3">
              <div className="flex items-center justify-between text-white/50 text-[10px] px-2 font-mono">
                <span>9:41 AM</span>
                <span>KaamSetu Mobile</span>
              </div>

              {/* Notification Card Component */}
              <div className="bg-white/95 backdrop-blur-md rounded-2xl p-3.5 text-xs space-y-2 border border-white/20 shadow-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-lg bg-[#2563EB] flex items-center justify-center text-white text-[10px] font-bold">
                      KS
                    </div>
                    <span className="font-extrabold text-[#0F172A] text-[11px]">
                      KaamSetu • {previewTab}
                    </span>
                  </div>
                  <span className="text-[10px] text-[#94A3B8]">Just now</span>
                </div>

                <div className="space-y-1">
                  <h4 className="font-extrabold text-[#0F172A] text-xs leading-snug">
                    {title || 'Sample Notification Title'}
                  </h4>
                  <p className="text-[11px] text-[#475569] leading-relaxed">
                    {shortMessage ||
                      'Your push message short summary will appear here on user screens.'}
                  </p>
                </div>

                {bannerUrl && (
                  <img
                    src={bannerUrl}
                    alt="Banner preview"
                    className="w-full h-24 rounded-lg object-cover border border-[#E2E8F0]"
                  />
                )}

                <div className="pt-1 flex items-center justify-between border-t border-[#F1F5F9]">
                  <span className="text-[10px] font-extrabold text-[#2563EB]">
                    {actionLabel || 'View Details'} →
                  </span>
                  <span className="text-[9px] text-[#94A3B8] uppercase">
                    {notificationType}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* RECENT BROADCASTS SUMMARY */}
          <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
            <h3 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider">
              Recent Broadcast Announcements
            </h3>

            <div className="space-y-3 max-h-80 overflow-y-auto pr-1">
              {recentBroadcasts.map((brd) => (
                <div
                  key={brd.id}
                  className="p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl space-y-1"
                >
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="font-bold text-[#0F172A] truncate max-w-[70%]">
                      {brd.title}
                    </span>
                    <span
                      className={`px-2 py-0.2 rounded text-[9px] font-extrabold ${
                        brd.status === 'Sent'
                          ? 'bg-[#DCFCE7] text-[#16A34A]'
                          : 'bg-[#FEF3C7] text-[#D97706]'
                      }`}
                    >
                      {brd.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-[#64748B]">
                    <span>Target: {brd.audienceType}</span>
                    <span>~{brd.estimatedRecipients.toLocaleString()} users</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* CONFIRMATION MODAL */}
      <ConfirmModal
        isOpen={confirmModalOpen}
        onClose={() => setConfirmModalOpen(false)}
        onConfirm={handleSendBroadcast}
        title={
          scheduleType === 'Now'
            ? 'Dispatch Broadcast Notification?'
            : 'Schedule Broadcast Announcement?'
        }
        message={`Are you sure you want to send this broadcast notification to approximately ~${estimatedRecipients.toLocaleString()} users? (Frontend demo action)`}
        confirmText={
          scheduleType === 'Now' ? 'Send Now' : 'Schedule Broadcast'
        }
        type="info"
      />
    </PageContainer>
  );
}
