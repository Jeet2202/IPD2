export const REVENUE_SUMMARY = {
  grossTransactionValue: 1248500,
  platformRevenue: 124850,
  workerEarnings: 1123650,
  refundedAmount: 38250,
  netPlatformRevenue: 86600,
};

export const REVENUE_TREND_CHART = [
  { date: '25 Jul', gross: 185000, platformRevenue: 18500, workerEarnings: 166500 },
  { date: '26 Jul', gross: 210000, platformRevenue: 21000, workerEarnings: 189000 },
  { date: '27 Jul', gross: 165000, platformRevenue: 16500, workerEarnings: 148500 },
  { date: '28 Jul', gross: 195000, platformRevenue: 19500, workerEarnings: 175500 },
  { date: '29 Jul', gross: 220000, platformRevenue: 22000, workerEarnings: 198000 },
  { date: '30 Jul', gross: 178000, platformRevenue: 17800, workerEarnings: 160200 },
  { date: '31 Jul', gross: 245000, platformRevenue: 24500, workerEarnings: 220500 },
];

export const REVENUE_BY_SOURCE = [
  { source: 'Normal Jobs', gross: 650000, platformShare: 65000, workerShare: 585000 },
  { source: 'Inspection Visiting Charges', gross: 42500, platformShare: 4250, workerShare: 38250 },
  { source: 'Inspection Repair Jobs', gross: 556000, platformShare: 55600, workerShare: 500400 },
];

export const REVENUE_BY_CATEGORY = [
  { category: 'Electrical', gross: 385000, platformShare: 38500 },
  { category: 'Plumbing', gross: 245000, platformShare: 24500 },
  { category: 'AC & Appliance Repair', gross: 280000, platformShare: 28000 },
  { category: 'Carpentry', gross: 165000, platformShare: 16500 },
  { category: 'Painting', gross: 98000, platformShare: 9800 },
  { category: 'Cleaning', gross: 75500, platformShare: 7550 },
];

export const REVENUE_TRANSACTIONS = [
  { date: '31 Jul', referenceId: 'JOB-10284', type: 'Normal Job', grossAmount: 850, workerShare: 765, platformShare: 85, refundAdjustment: 0, netRevenue: 85 },
  { date: '31 Jul', referenceId: 'INS-50124', type: 'Inspection Visit', grossAmount: 99, workerShare: 89, platformShare: 10, refundAdjustment: 0, netRevenue: 10 },
  { date: '31 Jul', referenceId: 'JOB-10270', type: 'Inspection Repair', grossAmount: 3400, workerShare: 3060, platformShare: 340, refundAdjustment: 0, netRevenue: 340 },
  { date: '30 Jul', referenceId: 'JOB-10255', type: 'Normal Job', grossAmount: 750, workerShare: 675, platformShare: 75, refundAdjustment: 200, netRevenue: -125 },
];
