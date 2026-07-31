export const COMMISSION_RULES = {
  globalDefault: {
    commissionType: 'Percentage',
    commissionValue: 10,
    effectiveFrom: '2026-01-01',
    status: 'Active',
    description: 'Demo configuration — not final business policy.',
  },
  categoryRules: [
    { id: 'COM-101', category: 'Electrical', commissionType: 'Percentage', commissionValue: 10, status: 'Active', updatedAt: '2026-07-01' },
    { id: 'COM-102', category: 'Plumbing', commissionType: 'Percentage', commissionValue: 10, status: 'Active', updatedAt: '2026-07-01' },
    { id: 'COM-103', category: 'AC & Appliance Repair', commissionType: 'Percentage', commissionValue: 12, status: 'Active', updatedAt: '2026-07-15' },
    { id: 'COM-104', category: 'Carpentry', commissionType: 'Percentage', commissionValue: 10, status: 'Active', updatedAt: '2026-07-01' },
    { id: 'COM-105', category: 'Painting', commissionType: 'Percentage', commissionValue: 8, status: 'Active', updatedAt: '2026-07-10' },
    { id: 'COM-106', category: 'Cleaning', commissionType: 'Percentage', commissionValue: 15, status: 'Active', updatedAt: '2026-07-20' },
  ],
  inspectionVisitCommission: {
    visitingCharge: 100,
    workerShare: 90,
    platformShare: 10,
    description: 'Demo values — inspection visiting charge split.',
  },
};
