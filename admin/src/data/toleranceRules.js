export const GLOBAL_TOLERANCE_RULE = {
  toleranceType: 'Fixed Amount', // Fixed Amount | Percentage
  toleranceValue: 100,
  aboveRangeAction: 'Flag for Review', // Flag for Review | Cap to Platform Maximum | Require Customer Confirmation
  status: 'Active',
  description: 'Professional quotation may exceed the configured maximum market price by up to ₹100 before being flagged for audit.',
};

export const TOLERANCE_RULES_DATA = [
  {
    id: 'TOL-101',
    categoryId: 'CAT-101',
    categoryName: 'Electrical',
    toleranceType: 'Fixed Amount',
    toleranceValue: 100,
    aboveRangeAction: 'Flag for Review',
    status: 'Active',
    autoAcceptRange: '≤ Max + ₹100',
    updatedAt: '2026-07-28',
  },
  {
    id: 'TOL-102',
    categoryId: 'CAT-102',
    categoryName: 'Plumbing',
    toleranceType: 'Percentage',
    toleranceValue: 10,
    aboveRangeAction: 'Flag for Review',
    status: 'Active',
    autoAcceptRange: '≤ Max + 10%',
    updatedAt: '2026-07-28',
  },
  {
    id: 'TOL-103',
    categoryId: 'CAT-105',
    categoryName: 'AC & Appliance Repair',
    toleranceType: 'Fixed Amount',
    toleranceValue: 200,
    aboveRangeAction: 'Require Customer Confirmation',
    status: 'Active',
    autoAcceptRange: '≤ Max + ₹200',
    updatedAt: '2026-07-30',
  },
];
