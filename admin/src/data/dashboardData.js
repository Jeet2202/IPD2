export const DASHBOARD_STATS = {
  totalCustomers: 12480,
  verifiedWorkers: 3240,
  activeJobs: 486,
  pendingVerifications: 72,
  todaysJobs: 142,
  inspectionRequests: 38,
  pendingComplaints: 9,
  completedJobsToday: 94,
};

export const WEEKLY_JOB_TRENDS = [
  { day: 'Mon', normalJobs: 110, inspectionRequests: 28 },
  { day: 'Tue', normalJobs: 135, inspectionRequests: 34 },
  { day: 'Wed', normalJobs: 128, inspectionRequests: 30 },
  { day: 'Thu', normalJobs: 152, inspectionRequests: 42 },
  { day: 'Fri', normalJobs: 178, inspectionRequests: 49 },
  { day: 'Sat', normalJobs: 215, inspectionRequests: 62 },
  { day: 'Sun', normalJobs: 195, inspectionRequests: 54 },
];

export const PLATFORM_ACTIVITY = [
  { category: 'Normal Requests', count: 1113 },
  { category: 'Inspection Requests', count: 299 },
  { category: 'Completed Jobs', count: 1240 },
  { category: 'Cancelled Jobs', count: 68 },
];

export const PENDING_VERIFICATIONS_SUMMARY = [
  {
    id: 'WRK-2005',
    worker: 'Suresh Mechanic',
    profession: 'Mechanic',
    submitted: 'Today',
    status: 'Pending',
  },
  {
    id: 'WRK-2007',
    worker: 'Mohan Lal Cleaner',
    profession: 'Cleaner',
    submitted: 'Yesterday',
    status: 'Pending',
  },
  {
    id: 'WRK-2010',
    worker: 'Karan Sharma',
    profession: 'Electrician',
    submitted: '2 days ago',
    status: 'Pending',
  },
  {
    id: 'WRK-2012',
    worker: 'Nitin Rao',
    profession: 'Plumber',
    submitted: '3 days ago',
    status: 'Pending',
  },
];

export const RECENT_JOBS = [
  {
    id: 'JOB-9842',
    customer: 'Ananya Sharma',
    service: 'MCB Replacement & DB Wiring',
    worker: 'Sunil Verma',
    type: 'Normal',
    amount: '₹850',
    status: 'In Progress',
  },
  {
    id: 'INSP-4109',
    customer: 'Vikramaditya Roy',
    service: 'AC Cooling Leakage Inspection',
    worker: 'Amit Patel',
    type: 'Inspection',
    amount: '₹99',
    status: 'Assigned',
  },
  {
    id: 'JOB-9841',
    customer: 'Pooja Hegde',
    service: 'Furniture Hinge Fixing',
    worker: 'Ramesh Carpenter',
    type: 'Normal',
    amount: '₹750',
    status: 'Completed',
  },
  {
    id: 'JOB-9840',
    customer: 'Siddharth Nair',
    service: 'Tap Leakage & Flush Tank Fix',
    worker: 'Rajesh Kumar',
    type: 'Normal',
    amount: '₹650',
    status: 'Searching',
  },
];

export const ADMIN_ATTENTION_ITEMS = [
  {
    id: 1,
    title: '12 quotations flagged for high pricing tolerance',
    type: 'warning',
    link: '/admin/quotations',
  },
  {
    id: 2,
    title: '8 worker documents require KYC review',
    type: 'info',
    link: '/admin/verification',
  },
  {
    id: 3,
    title: '5 complaints marked high priority',
    type: 'danger',
    link: '/admin/complaints',
  },
  {
    id: 4,
    title: '18 inspection reports awaiting processing',
    type: 'info',
    link: '/admin/inspections',
  },
];
