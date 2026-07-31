export const PAYMENTS_SUMMARY = {
  totalVolume: 1248500,
  platformRevenue: 124850,
  pendingPayouts: 218400,
  refunds: 38250,
  successfulPayments: 486,
  pendingPayments: 12,
  failedPayments: 3,
  refundedPayments: 8,
};

export const PAYMENT_VOLUME_CHART = [
  { date: '25 Jul', customerPayments: 185000, workerPayouts: 166500, refunds: 4200 },
  { date: '26 Jul', customerPayments: 210000, workerPayouts: 189000, refunds: 6800 },
  { date: '27 Jul', customerPayments: 165000, workerPayouts: 148500, refunds: 3100 },
  { date: '28 Jul', customerPayments: 195000, workerPayouts: 175500, refunds: 5500 },
  { date: '29 Jul', customerPayments: 220000, workerPayouts: 198000, refunds: 7200 },
  { date: '30 Jul', customerPayments: 178000, workerPayouts: 160200, refunds: 4800 },
  { date: '31 Jul', customerPayments: 245000, workerPayouts: 220500, refunds: 6650 },
];

export const PAYMENT_SOURCE_BREAKDOWN = [
  { source: 'Normal Jobs', amount: 650000, percentage: 52 },
  { source: 'Inspection Visiting Charges', amount: 42500, percentage: 3.4 },
  { source: 'Inspection Repair Jobs', amount: 556000, percentage: 44.6 },
];

export const RECENT_TRANSACTIONS_PREVIEW = [
  {
    id: 'TXN-90128',
    customerName: 'Ananya Sharma',
    type: 'Normal Job Payment',
    reference: 'JOB-10284',
    amount: 850,
    method: 'UPI (GPay)',
    status: 'Successful',
    time: '31 Jul, 2:15 PM',
  },
  {
    id: 'TXN-90129',
    customerName: 'Vikramaditya Roy',
    type: 'Inspection Visiting Charge',
    reference: 'INS-50124',
    amount: 99,
    method: 'UPI (PhonePe)',
    status: 'Successful',
    time: '31 Jul, 11:02 AM',
  },
  {
    id: 'TXN-90130',
    customerName: 'Vikramaditya Roy',
    type: 'Inspection Repair Payment',
    reference: 'JOB-10270',
    amount: 3400,
    method: 'Card (HDFC)',
    status: 'Pending',
    time: '31 Jul, 4:30 PM',
  },
  {
    id: 'TXN-90131',
    customerName: 'Pooja Hegde',
    type: 'Normal Job Payment',
    reference: 'JOB-10255',
    amount: 750,
    method: 'UPI (PhonePe)',
    status: 'Successful',
    time: '30 Jul, 10:20 AM',
  },
];

export const PENDING_PAYOUTS_PREVIEW = [
  { workerName: 'Sunil Verma', amount: 7650, jobs: 4, eligibleDate: '1 Aug 2026', status: 'Eligible' },
  { workerName: 'Amit Patel', amount: 12800, jobs: 6, eligibleDate: '1 Aug 2026', status: 'Processing' },
  { workerName: 'Ramesh Carpenter', amount: 5400, jobs: 3, eligibleDate: '2 Aug 2026', status: 'Eligible' },
];

export const ATTENTION_REQUIRED = {
  failedPayments: 3,
  refundPending: 5,
  payoutFailed: 1,
  paymentDisputes: 2,
};
