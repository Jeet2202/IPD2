import React, { useState } from 'react';
import {
  Settings as SettingsIcon,
  Globe,
  Briefcase,
  IndianRupee,
  Bell,
  ShieldCheck,
  AlertTriangle,
  Palette,
  Save,
  CheckCircle2,
  Lock,
  Mail,
  Phone,
  Clock,
  Building,
  Image as ImageIcon,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import ToggleCard from '../../components/common/ToggleCard';
import { useToast } from '../../components/common/ToastContext';
import { INITIAL_PLATFORM_SETTINGS } from '../../data/settings';

export default function Settings() {
  const { addToast } = useToast();
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState(INITIAL_PLATFORM_SETTINGS);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const sections = [
    { id: 'general', label: 'General', icon: Globe },
    { id: 'business', label: 'Business', icon: Briefcase },
    { id: 'pricing', label: 'Pricing', icon: IndianRupee },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: ShieldCheck },
    { id: 'maintenance', label: 'Maintenance', icon: AlertTriangle },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ];

  const handleSave = (e) => {
    e?.preventDefault();
    setSavedSuccess(true);
    addToast({
      title: 'Settings Saved',
      message: 'Global platform configuration updated successfully.',
      type: 'success',
    });
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <PageContainer
      title="Platform Settings"
      subtitle="Global configuration settings for KaamSetu ecosystem operations."
      action={
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl transition-colors shadow-xs"
        >
          {savedSuccess ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-white" />
              <span>Saved!</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>Save Configuration</span>
            </>
          )}
        </button>
      }
    >
      <div className="space-y-6">
        {/* Success Toast Banner */}
        {savedSuccess && (
          <div className="p-4 rounded-xl bg-[#DCFCE7] border border-[#BBF7D0] flex items-center justify-between text-xs font-bold text-[#166534] animate-fadeIn">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-[#16A34A]" />
              <span>Platform configuration updated successfully. All parameters applied.</span>
            </div>
          </div>
        )}

        {/* ── SETTINGS TABS & CONTENT ───────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Tabs */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-3 shadow-xs space-y-1 h-fit">
            {sections.map((sec) => {
              const Icon = sec.icon;
              const isActive = activeTab === sec.id;
              return (
                <button
                  key={sec.id}
                  onClick={() => setActiveTab(sec.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-[#2563EB] text-white shadow-xs'
                      : 'text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{sec.label}</span>
                </button>
              );
            })}
          </div>

          {/* Main Form Content */}
          <div className="lg:col-span-3 bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs">
            {/* 1. GENERAL SECTION */}
            {activeTab === 'general' && (
              <form onSubmit={handleSave} className="space-y-5 text-xs">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">General Settings</h3>
                  <p className="text-xs text-[#64748B]">Core identity, brand branding & contact details</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Platform Name</label>
                    <input
                      type="text"
                      value={settings.general.platformName}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, platformName: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Timezone</label>
                    <input
                      type="text"
                      value={settings.general.timezone}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, timezone: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Support Email</label>
                    <input
                      type="email"
                      value={settings.general.supportEmail}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, supportEmail: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Support Phone</label>
                    <input
                      type="text"
                      value={settings.general.supportPhone}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, supportPhone: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Currency Symbol</label>
                    <input
                      type="text"
                      value={settings.general.currency}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, currency: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">System Language</label>
                    <input
                      type="text"
                      value={settings.general.language}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          general: { ...settings.general, language: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>
                </div>
              </form>
            )}

            {/* 2. BUSINESS SECTION */}
            {activeTab === 'business' && (
              <form onSubmit={handleSave} className="space-y-5 text-xs">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">Business Profile</h3>
                  <p className="text-xs text-[#64748B]">Legal corporate registration & operational details</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Business Registered Name</label>
                    <input
                      type="text"
                      value={settings.business.businessName}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          business: { ...settings.business, businessName: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">GST Registration Number</label>
                    <input
                      type="text"
                      value={settings.business.gstNumber}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          business: { ...settings.business, gstNumber: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Registered HQ Address</label>
                    <textarea
                      rows={3}
                      value={settings.business.registeredAddress}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          business: { ...settings.business, registeredAddress: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Customer Support Operating Hours</label>
                    <input
                      type="text"
                      value={settings.business.supportHours}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          business: { ...settings.business, supportHours: e.target.value },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>
                </div>
              </form>
            )}

            {/* 3. PRICING SECTION */}
            {activeTab === 'pricing' && (
              <form onSubmit={handleSave} className="space-y-5 text-xs">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">Pricing & Fee Defaults</h3>
                  <p className="text-xs text-[#64748B]">Platform commissions, GST tax rates & inspection defaults</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Default Tax Rate (GST %)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={settings.pricing.defaultTaxRate}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          pricing: { ...settings.pricing, defaultTaxRate: parseFloat(e.target.value) },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Platform Commission Fee (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={settings.pricing.defaultPlatformCommission}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          pricing: { ...settings.pricing, defaultPlatformCommission: parseFloat(e.target.value) },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Default Inspection Fee (₹)</label>
                    <input
                      type="number"
                      value={settings.pricing.inspectionFeeDefault}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          pricing: { ...settings.pricing, inspectionFeeDefault: parseInt(e.target.value, 10) },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>
                </div>

                <ToggleCard
                  title="Visiting Charge Deductible / Refundable"
                  description="Automatically deduct inspection fee from final quotation total when customer accepts job."
                  checked={settings.pricing.visitingChargeRefundable}
                  onChange={(val) =>
                    setSettings({
                      ...settings,
                      pricing: { ...settings.pricing, visitingChargeRefundable: val },
                    })
                  }
                  icon={IndianRupee}
                />
              </form>
            )}

            {/* 4. NOTIFICATIONS SECTION */}
            {activeTab === 'notifications' && (
              <div className="space-y-4">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">Notification Toggles</h3>
                  <p className="text-xs text-[#64748B]">Channel dispatch preferences & alert rules</p>
                </div>

                <div className="space-y-3">
                  <ToggleCard
                    title="Email Alerts Channel"
                    description="Dispatch operational summary and invoice receipts via Email."
                    checked={settings.notifications.emailNotifications}
                    onChange={(val) =>
                      setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, emailNotifications: val },
                      })
                    }
                    icon={Mail}
                  />

                  <ToggleCard
                    title="SMS Gateway Channel"
                    description="Send transactional OTPs and booking updates via SMS."
                    checked={settings.notifications.smsNotifications}
                    onChange={(val) =>
                      setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, smsNotifications: val },
                      })
                    }
                    icon={Phone}
                  />

                  <ToggleCard
                    title="Mobile Push Notifications"
                    description="Push instant status alerts to Flutter Customer/Worker applications."
                    checked={settings.notifications.pushNotifications}
                    onChange={(val) =>
                      setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, pushNotifications: val },
                      })
                    }
                    icon={Bell}
                  />

                  <ToggleCard
                    title="In-App Admin Notifications"
                    description="Display popups & notification bell badges within Admin Dashboard."
                    checked={settings.notifications.inAppNotifications}
                    onChange={(val) =>
                      setSettings({
                        ...settings,
                        notifications: { ...settings.notifications, inAppNotifications: val },
                      })
                    }
                    icon={Bell}
                  />
                </div>
              </div>
            )}

            {/* 5. SECURITY SECTION */}
            {activeTab === 'security' && (
              <form onSubmit={handleSave} className="space-y-5 text-xs">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">Security Controls</h3>
                  <p className="text-xs text-[#64748B]">Session timeouts, 2FA & password policies</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Session Idle Timeout (Minutes)</label>
                    <input
                      type="number"
                      value={settings.security.sessionTimeoutMinutes}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          security: { ...settings.security, sessionTimeoutMinutes: parseInt(e.target.value, 10) },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#0F172A] mb-1">Max Failed Login Attempts</label>
                    <input
                      type="number"
                      value={settings.security.maxLoginAttempts}
                      onChange={(e) =>
                        setSettings({
                          ...settings,
                          security: { ...settings.security, maxLoginAttempts: parseInt(e.target.value, 10) },
                        })
                      }
                      className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                    />
                  </div>
                </div>

                <ToggleCard
                  title="Require Two-Factor Authentication (2FA)"
                  description="Enforce OTP verification for all Super Admin & Finance login sessions."
                  checked={settings.security.requireTwoFactorAuth}
                  onChange={(val) =>
                    setSettings({
                      ...settings,
                      security: { ...settings.security, requireTwoFactorAuth: val },
                    })
                  }
                  icon={ShieldCheck}
                />
              </form>
            )}

            {/* 6. MAINTENANCE SECTION */}
            {activeTab === 'maintenance' && (
              <div className="space-y-5 text-xs">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">Platform Maintenance Mode</h3>
                  <p className="text-xs text-[#64748B]">Emergency downtime switch & scheduled banner messages</p>
                </div>

                <ToggleCard
                  title="Enable Maintenance Mode"
                  description="Temporarily pause new customer bookings and restrict worker app sync."
                  checked={settings.maintenance.maintenanceMode}
                  onChange={(val) =>
                    setSettings({
                      ...settings,
                      maintenance: { ...settings.maintenance, maintenanceMode: val },
                    })
                  }
                  icon={AlertTriangle}
                />

                <div>
                  <label className="block text-xs font-bold text-[#0F172A] mb-1">Maintenance Banner Message</label>
                  <textarea
                    rows={3}
                    value={settings.maintenance.maintenanceMessage}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        maintenance: { ...settings.maintenance, maintenanceMessage: e.target.value },
                      })
                    }
                    className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] focus:border-[#2563EB] outline-none"
                  />
                </div>
              </div>
            )}

            {/* 7. APPEARANCE SECTION */}
            {activeTab === 'appearance' && (
              <div className="space-y-5 text-xs">
                <div className="border-b border-[#F1F5F9] pb-3">
                  <h3 className="text-base font-extrabold text-[#0F172A]">Appearance & UI Theme</h3>
                  <p className="text-xs text-[#64748B]">Admin dashboard visual preferences</p>
                </div>

                <div className="space-y-3">
                  <label className="block text-xs font-bold text-[#0F172A]">Color Theme</label>
                  <div className="grid grid-cols-3 gap-3">
                    {['light', 'dark', 'system'].map((th) => (
                      <button
                        key={th}
                        onClick={() =>
                          setSettings({
                            ...settings,
                            appearance: { ...settings.appearance, theme: th },
                          })
                        }
                        className={`p-3 rounded-xl border text-center capitalize font-bold text-xs transition-all ${
                          settings.appearance.theme === th
                            ? 'border-[#2563EB] bg-[#EFF6FF] text-[#2563EB]'
                            : 'border-[#E2E8F0] bg-white text-[#475569] hover:bg-[#F8FAFC]'
                        }`}
                      >
                        {th} Theme
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="block text-xs font-bold text-[#0F172A]">Sidebar Layout</label>
                  <div className="grid grid-cols-2 gap-3">
                    {['default', 'compact'].map((st) => (
                      <button
                        key={st}
                        onClick={() =>
                          setSettings({
                            ...settings,
                            appearance: { ...settings.appearance, sidebarStyle: st },
                          })
                        }
                        className={`p-3 rounded-xl border text-center capitalize font-bold text-xs transition-all ${
                          settings.appearance.sidebarStyle === st
                            ? 'border-[#2563EB] bg-[#EFF6FF] text-[#2563EB]'
                            : 'border-[#E2E8F0] bg-white text-[#475569] hover:bg-[#F8FAFC]'
                        }`}
                      >
                        {st} Sidebar
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
