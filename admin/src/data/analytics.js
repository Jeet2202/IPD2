// Dummy Data for Screen 36 - Analytics Dashboard

export const ANALYTICS_KPIS = {
  totalCustomers: 14280,
  totalCustomersChange: '+14.2%',
  totalWorkers: 3850,
  totalWorkersChange: '+8.5%',
  verifiedWorkers: 3420,
  verifiedWorkersChange: '+9.1%',
  activeJobs: 184,
  activeJobsChange: '+12.0%',
  completedJobs: 24650,
  completedJobsChange: '+18.4%',
  inspectionRequests: 890,
  inspectionRequestsChange: '+15.3%',
  revenue: 3485000,
  revenueChange: '+22.6%',
  avgRating: 4.82,
  avgRatingChange: '+0.15',
};

export const CUSTOMER_GROWTH_DATA = [
  { month: 'Jan', customers: 8200, newCustomers: 650 },
  { month: 'Feb', customers: 9100, newCustomers: 900 },
  { month: 'Mar', customers: 10050, newCustomers: 950 },
  { month: 'Apr', customers: 11200, newCustomers: 1150 },
  { month: 'May', customers: 12400, newCustomers: 1200 },
  { month: 'Jun', customers: 13500, newCustomers: 1100 },
  { month: 'Jul', customers: 14280, newCustomers: 780 },
];

export const WORKER_GROWTH_DATA = [
  { month: 'Jan', total: 2100, verified: 1850 },
  { month: 'Feb', total: 2450, verified: 2150 },
  { month: 'Mar', total: 2800, verified: 2480 },
  { month: 'Apr', total: 3150, verified: 2800 },
  { month: 'May', total: 3450, verified: 3080 },
  { month: 'Jun', total: 3680, verified: 3290 },
  { month: 'Jul', total: 3850, verified: 3420 },
];

export const DAILY_BOOKINGS_DATA = [
  { day: 'Mon', normal: 145, inspection: 32 },
  { day: 'Tue', normal: 168, inspection: 41 },
  { day: 'Wed', normal: 180, inspection: 38 },
  { day: 'Thu', normal: 195, inspection: 45 },
  { day: 'Fri', normal: 210, inspection: 52 },
  { day: 'Sat', normal: 250, inspection: 68 },
  { day: 'Sun', normal: 220, inspection: 58 },
];

export const REVENUE_TREND_DATA = [
  { month: 'Jan', platformFee: 180000, inspectionFee: 45000, total: 225000 },
  { month: 'Feb', platformFee: 220000, inspectionFee: 58000, total: 278000 },
  { month: 'Mar', platformFee: 260000, inspectionFee: 72000, total: 332000 },
  { month: 'Apr', platformFee: 310000, inspectionFee: 85000, total: 395000 },
  { month: 'May', platformFee: 380000, inspectionFee: 105000, total: 485000 },
  { month: 'Jun', platformFee: 440000, inspectionFee: 128000, total: 568000 },
  { month: 'Jul', platformFee: 510000, inspectionFee: 145000, total: 655000 },
];

export const SERVICE_CATEGORY_DISTRIBUTION = [
  { name: 'Electrical', value: 32, jobs: 7890, revenue: 1115000, workers: 950, rating: 4.8 },
  { name: 'Plumbing', value: 24, jobs: 5910, revenue: 836000, workers: 720, rating: 4.7 },
  { name: 'Carpentry', value: 16, jobs: 3940, revenue: 558000, workers: 480, rating: 4.8 },
  { name: 'Painting', value: 12, jobs: 2950, revenue: 418000, workers: 360, rating: 4.9 },
  { name: 'Cleaning', value: 8, jobs: 1970, revenue: 279000, workers: 240, rating: 4.6 },
  { name: 'Mechanic', value: 5, jobs: 1230, revenue: 174000, workers: 150, rating: 4.7 },
  { name: 'AC Repair', value: 3, jobs: 760, revenue: 105000, workers: 90, rating: 4.9 },
];

export const JOBS_BY_CITY = [
  { city: 'Mumbai', customers: 5800, workers: 1450, jobs: 10200, revenue: 1450000 },
  { city: 'Pune', customers: 3400, workers: 920, jobs: 5800, revenue: 820000 },
  { city: 'Navi Mumbai', customers: 2100, workers: 610, jobs: 3900, revenue: 540000 },
  { city: 'Thane', customers: 1850, workers: 520, jobs: 3100, revenue: 420000 },
  { city: 'Nagpur', customers: 1130, workers: 350, jobs: 1650, revenue: 255000 },
];

export const WORKER_PERFORMANCE_METRICS = {
  topWorkers: [
    { id: 'WRK-1001', name: 'Rajesh Sharma', category: 'Electrician', rating: 4.98, jobs: 342, earnings: '₹1,84,500' },
    { id: 'WRK-1008', name: 'Amit Varma', category: 'Plumber', rating: 4.95, jobs: 298, earnings: '₹1,62,000' },
    { id: 'WRK-1014', name: 'Vikram Singh', category: 'Carpenter', rating: 4.92, jobs: 275, earnings: '₹1,51,200' },
    { id: 'WRK-1022', name: 'Sanjay Kumar', category: 'AC Technician', rating: 4.90, jobs: 240, earnings: '₹1,45,000' },
  ],
  lowestRatedWorkers: [
    { id: 'WRK-1099', name: 'Rohan Shinde', category: 'Painter', rating: 3.42, jobs: 18, warnings: 2 },
    { id: 'WRK-1104', name: 'Deepak Thorat', category: 'Plumber', rating: 3.65, jobs: 24, warnings: 1 },
    { id: 'WRK-1112', name: 'Karan Malhotra', category: 'Electrician', rating: 3.78, jobs: 31, warnings: 1 },
  ],
  mostActiveWorkers: [
    { id: 'WRK-1001', name: 'Rajesh Sharma', activeHours: '48 hrs/wk', completedThisMonth: 42 },
    { id: 'WRK-1008', name: 'Amit Varma', activeHours: '44 hrs/wk', completedThisMonth: 38 },
    { id: 'WRK-1015', name: 'Sunil Pawar', activeHours: '42 hrs/wk', completedThisMonth: 36 },
  ],
  mostCancelledJobs: [
    { id: 'WRK-1120', name: 'Prakash Patil', cancellations: 8, reason: 'Worker Unresponsive' },
    { id: 'WRK-1125', name: 'Ganesh More', cancellations: 6, reason: 'Delayed Arrival' },
  ],
};

export const CUSTOMER_ANALYTICS_DATA = {
  mostActiveCustomers: [
    { id: 'CUST-2001', name: 'Rahul Deshmukh', city: 'Mumbai', bookings: 28, totalSpent: '₹42,500' },
    { id: 'CUST-2015', name: 'Priya Kulkarni', city: 'Pune', bookings: 24, totalSpent: '₹38,200' },
    { id: 'CUST-2042', name: 'Sneha Mehta', city: 'Navi Mumbai', bookings: 21, totalSpent: '₹31,900' },
  ],
  repeatCustomersCount: 8940,
  repeatCustomersRate: '62.6%',
  inspectionHeavyCustomers: [
    { id: 'CUST-2088', name: 'Oberoi Heights RWA', city: 'Mumbai', inspections: 14, convertedJobs: 12 },
    { id: 'CUST-2102', name: 'Greenfield Apartments', city: 'Thane', inspections: 11, convertedJobs: 9 },
  ],
};

export const BOOKING_ANALYTICS = {
  normalRequests: 18450,
  inspectionRequests: 3200,
  completed: 19480,
  pending: 1250,
  cancelled: 920,
  completionRate: '94.8%',
};
