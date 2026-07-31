// Dummy Data for Screen 40 - Platform Settings

export const INITIAL_PLATFORM_SETTINGS = {
  general: {
    platformName: 'KaamSetu Admin',
    logoUrl: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100',
    supportEmail: 'support@kaamsetu.com',
    supportPhone: '+91 1800-572-8800',
    timezone: 'Asia/Kolkata (IST +5:30)',
    currency: 'INR (₹)',
    language: 'English (US)',
  },
  business: {
    businessName: 'KaamSetu Hyperlocal Technologies Pvt. Ltd.',
    gstNumber: '27AAACK1234F1Z8',
    registeredAddress: 'Level 8, Commerce Tower, Bandra-Kurla Complex (BKC), Mumbai, MH - 400051',
    supportHours: 'Monday - Sunday: 8:00 AM - 10:00 PM IST',
  },
  pricing: {
    defaultCurrency: 'INR (₹)',
    defaultTaxRate: 18.0, // GST percentage
    defaultPlatformCommission: 12.5, // Percentage
    inspectionFeeDefault: 299, // Base visiting / inspection charge in INR
    visitingChargeRefundable: true,
  },
  notifications: {
    emailNotifications: true,
    smsNotifications: true,
    pushNotifications: true,
    inAppNotifications: true,
    notifyOnNewJob: true,
    notifyOnWorkerSignup: true,
    notifyOnHighValueRefund: true,
  },
  security: {
    sessionTimeoutMinutes: 60,
    passwordExpiryDays: 90,
    requireTwoFactorAuth: true,
    maxLoginAttempts: 5,
    ipWhitelistingEnabled: false,
  },
  maintenance: {
    maintenanceMode: false,
    maintenanceMessage: 'KaamSetu platform is undergoing scheduled routine maintenance. Operations will resume shortly.',
    scheduledStartTime: '2026-08-05T02:00',
    scheduledEndTime: '2026-08-05T04:00',
  },
  appearance: {
    theme: 'light', // light, dark, system
    sidebarStyle: 'default', // default, compact
    accentColor: '#2563EB', // Blue
  },
};
