import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  CheckCheck,
  Megaphone,
  BadgeCheck,
  ShieldAlert,
  MessageSquareWarning,
  CreditCard,
  AlertCircle,
  Clock,
  Trash2,
  Check,
  ExternalLink,
  Sliders,
  Filter,
} from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';
import PriorityBadge from '../../components/common/PriorityBadge';
import EmptyState from '../../components/common/EmptyState';
import Modal from '../../components/common/Modal';
import { useToast } from '../../components/common/ToastContext';
import { NOTIFICATIONS_DATA } from '../../data/notifications';

export default function Notifications() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [notifications, setNotifications] = useState(NOTIFICATIONS_DATA);
  const [activeTab, setActiveTab] = useState('All'); // All | Unread | Verification | Pricing | Complaints | Payments | System

  const [settingsModalOpen, setSettingsModalOpen] = useState(false);

  // Unread count
  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.read).length,
    [notifications]
  );

  // Filtered Notifications List
  const filteredNotifications = useMemo(() => {
    return notifications.filter((n) => {
      if (activeTab === 'Unread') return !n.read;
      if (activeTab === 'Verification') return n.type === 'Verification';
      if (activeTab === 'Pricing') return n.type === 'Pricing';
      if (activeTab === 'Complaints') return n.type === 'Complaints';
      if (activeTab === 'Payments') return n.type === 'Payments';
      if (activeTab === 'System') return n.type === 'System';
      return true;
    });
  }, [notifications, activeTab]);

  const handleMarkAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    addToast({
      title: 'All Notifications Marked Read',
      message: 'Your operational inbox is updated.',
      type: 'success',
    });
  };

  const handleToggleRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: !n.read } : n))
    );
  };

  const handleDeleteNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
    addToast({
      title: 'Notification Dismissed',
      message: 'Alert removed from list.',
      type: 'info',
    });
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'Verification':
        return <BadgeCheck className="w-5 h-5 text-[#2563EB]" />;
      case 'Pricing':
        return <ShieldAlert className="w-5 h-5 text-[#EA580C]" />;
      case 'Complaints':
        return <MessageSquareWarning className="w-5 h-5 text-[#DC2626]" />;
      case 'Payments':
        return <CreditCard className="w-5 h-5 text-[#16A34A]" />;
      case 'System':
      default:
        return <AlertCircle className="w-5 h-5 text-[#9333EA]" />;
    }
  };

  const getNotificationBg = (type) => {
    switch (type) {
      case 'Verification':
        return 'bg-[#EFF6FF] border-[#BFDBFE]';
      case 'Pricing':
        return 'bg-[#FFF7ED] border-[#FFEDD5]';
      case 'Complaints':
        return 'bg-[#FEF2F2] border-[#FCA5A5]';
      case 'Payments':
        return 'bg-[#DCFCE7] border-[#BBF7D0]';
      case 'System':
      default:
        return 'bg-[#FAF5FF] border-[#E9D5FF]';
    }
  };

  return (
    <PageContainer
      title={
        <div className="flex items-center gap-3">
          <span>Admin Notification Center</span>
          {unreadCount > 0 && (
            <span className="px-2.5 py-0.5 rounded-full text-xs font-extrabold bg-[#EF4444] text-white">
              {unreadCount} Unread
            </span>
          )}
        </div>
      }
      subtitle="Stay updated on platform activity, disputes, verification requests and system alerts requiring administrative attention."
      action={
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSettingsModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-[#64748B] hover:text-[#0F172A] bg-white border border-[#E2E8F0] rounded-xl hover:bg-[#F8FAFC] transition-colors"
          >
            <Sliders className="w-3.5 h-3.5" />
            Alert Settings
          </button>
          <button
            onClick={handleMarkAllRead}
            disabled={unreadCount === 0}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold text-[#334155] bg-white border border-[#E2E8F0] hover:bg-[#F8FAFC] disabled:opacity-50 rounded-xl transition-colors shadow-2xs"
          >
            <CheckCheck className="w-3.5 h-3.5 text-[#16A34A]" />
            Mark All Read
          </button>
          <button
            onClick={() => navigate('/admin/notifications/broadcast')}
            className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl shadow-sm transition-colors"
          >
            <Megaphone className="w-3.5 h-3.5" />
            Create Broadcast
          </button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* CATEGORY TABS */}
        <div className="bg-white rounded-2xl p-2 border border-[#E2E8F0] shadow-2xs flex flex-wrap gap-1">
          {[
            { id: 'All', label: 'All Notifications' },
            { id: 'Unread', label: `Unread (${unreadCount})` },
            { id: 'Verification', label: 'Verification' },
            { id: 'Pricing', label: 'Pricing' },
            { id: 'Complaints', label: 'Complaints' },
            { id: 'Payments', label: 'Payments' },
            { id: 'System', label: 'System' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
                activeTab === tab.id
                  ? 'bg-[#2563EB] text-white shadow-sm'
                  : 'text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC]'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* NOTIFICATIONS LIST */}
        <div className="space-y-3">
          {filteredNotifications.length === 0 ? (
            <div className="bg-white rounded-2xl p-12 text-center border border-[#E2E8F0]">
              <EmptyState
                icon={Bell}
                title="You're all caught up!"
                description="No notifications match this filter criteria right now."
              />
            </div>
          ) : (
            filteredNotifications.map((notif) => (
              <div
                key={notif.id}
                className={`p-4 sm:p-5 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                  notif.read
                    ? 'bg-white border-[#E2E8F0]'
                    : 'bg-[#F8FAFC] border-[#2563EB]/40 shadow-2xs ring-1 ring-[#2563EB]/10'
                }`}
              >
                <div className="flex items-start gap-3.5">
                  {/* Icon Avatar */}
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center border shrink-0 ${getNotificationBg(
                      notif.type
                    )}`}
                  >
                    {getNotificationIcon(notif.type)}
                  </div>

                  {/* Text Content */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4
                        className={`text-sm font-extrabold ${
                          notif.read ? 'text-[#334155]' : 'text-[#0F172A]'
                        }`}
                      >
                        {notif.title}
                      </h4>
                      {!notif.read && (
                        <span className="w-2 h-2 rounded-full bg-[#2563EB] animate-pulse" />
                      )}
                      <PriorityBadge priority={notif.priority} />
                    </div>

                    <p className="text-xs text-[#64748B] leading-relaxed">
                      {notif.message}
                    </p>

                    <div className="flex items-center gap-3 pt-1 text-[11px] text-[#94A3B8]">
                      <span className="flex items-center gap-1 font-medium">
                        <Clock className="w-3 h-3" />
                        {notif.ageString}
                      </span>
                      {notif.referenceId && (
                        <span className="font-mono font-bold text-[#475569] bg-[#F1F5F9] px-2 py-0.5 rounded">
                          {notif.referenceId}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 shrink-0 border-t sm:border-t-0 pt-3 sm:pt-0 border-[#F1F5F9] justify-end">
                  {notif.actionRoute && (
                    <button
                      onClick={() => {
                        handleToggleRead(notif.id);
                        navigate(notif.actionRoute);
                      }}
                      className="px-3.5 py-2 text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl transition-colors flex items-center gap-1 shadow-2xs"
                    >
                      {notif.actionLabel || 'View Record'}{' '}
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  )}

                  <button
                    onClick={() => handleToggleRead(notif.id)}
                    className="p-2 text-[#64748B] hover:text-[#0F172A] hover:bg-[#F1F5F9] rounded-xl transition-colors"
                    title={notif.read ? 'Mark Unread' : 'Mark Read'}
                  >
                    <Check className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => handleDeleteNotification(notif.id)}
                    className="p-2 text-[#94A3B8] hover:text-[#DC2626] hover:bg-[#FEE2E2] rounded-xl transition-colors"
                    title="Dismiss Notification"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* NOTIFICATION SETTINGS MODAL PLACEHOLDER */}
      <Modal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
        title="Admin Alert Preferences"
      >
        <div className="space-y-4 py-2 text-xs">
          <p className="text-[#64748B]">
            Configure which operational events trigger instant admin alerts in this center.
          </p>

          <div className="space-y-3">
            {[
              { id: 's1', label: 'Flagged Inspection Pricing (>25% tolerance)', defaultChecked: true },
              { id: 's2', label: 'Urgent Complaints & Escalated Disputes', defaultChecked: true },
              { id: 's3', label: 'New Professional Verification Submissions', defaultChecked: true },
              { id: 's4', label: 'Failed Payout Batches & Refund Requests', defaultChecked: true },
              { id: 's5', label: 'High Cancellation Rate Alerts', defaultChecked: false },
            ].map((item) => (
              <label
                key={item.id}
                className="flex items-center justify-between p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl cursor-pointer"
              >
                <span className="font-semibold text-[#0F172A]">{item.label}</span>
                <input
                  type="checkbox"
                  defaultChecked={item.defaultChecked}
                  className="w-4 h-4 text-[#2563EB] rounded accent-[#2563EB]"
                />
              </label>
            ))}
          </div>

          <div className="flex justify-end pt-3 border-t border-[#E2E8F0]">
            <button
              onClick={() => {
                addToast({
                  title: 'Preferences Saved',
                  message: 'Admin alert triggers updated.',
                  type: 'success',
                });
                setSettingsModalOpen(false);
              }}
              className="px-4 py-2 text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl shadow-sm"
            >
              Save Preferences
            </button>
          </div>
        </div>
      </Modal>
    </PageContainer>
  );
}
