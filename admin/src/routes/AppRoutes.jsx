import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import AdminLayout from '../layouts/AdminLayout/AdminLayout';
import AuthLayout from '../layouts/AuthLayout/AuthLayout';

// Auth Pages
import AdminLogin from '../pages/auth/AdminLogin';

// Admin Core Pages (Screens 1 to 5)
import Dashboard from '../pages/dashboard/Dashboard';
import Customers from '../pages/customers/Customers';
import CustomerDetails from '../pages/customers/CustomerDetails';
import Workers from '../pages/workers/Workers';

// Admin Pages (Screens 6 to 10)
import WorkerDetails from '../pages/workers/WorkerDetails';
import VerificationRequests from '../pages/verification/VerificationRequests';
import VerificationReview from '../pages/verification/VerificationReview';
import ServiceCategories from '../pages/services/ServiceCategories';
import Services from '../pages/services/Services';

// Pricing Pages (Screens 11 to 15)
import MarketPriceGuide from '../pages/pricing/MarketPriceGuide';
import MarketPriceForm from '../pages/pricing/MarketPriceForm';
import VisitingCharges from '../pages/pricing/VisitingCharges';
import PriceIncreaseConfig from '../pages/pricing/PriceIncreaseConfig';
import PriceTolerance from '../pages/pricing/PriceTolerance';

// Operations Pages (Screens 16 to 20)
import Jobs from '../pages/jobs/Jobs';
import JobDetails from '../pages/jobs/JobDetails';
import InspectionRequests from '../pages/inspections/InspectionRequests';
import InspectionDetails from '../pages/inspections/InspectionDetails';
import InspectionReports from '../pages/inspections/InspectionReports';

// Inspection Audit & Quotations (Screens 21 to 25)
import InspectionReportDetails from '../pages/inspections/InspectionReportDetails';
import PriceAssessment from '../pages/inspections/PriceAssessment';
import FlaggedPricing from '../pages/inspections/FlaggedPricing';
import InspectionConversions from '../pages/inspections/InspectionConversions';
import Quotations from '../pages/quotations/Quotations';

// Finance Pages (Screens 26 to 30)
import PaymentsDashboard from '../pages/payments/PaymentsDashboard';
import Transactions from '../pages/payments/Transactions';
import WorkerPayouts from '../pages/payments/WorkerPayouts';
import Refunds from '../pages/payments/Refunds';
import Revenue from '../pages/payments/Revenue';

// Generic Fallback Placeholder for unbuilt pages
import PlaceholderPage from '../pages/common/PlaceholderPage';

export default function AppRoutes() {
  return (
    <Routes>
      {/* Root Redirection */}
      <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
      <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />

      {/* Auth Routes */}
      <Route path="/admin" element={<AuthLayout />}>
        <Route path="login" element={<AdminLogin />} />
      </Route>

      {/* Main Admin Application Routes (Screens 1 to 30) */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route path="dashboard" element={<Dashboard />} />
        
        {/* Customer Management */}
        <Route path="customers" element={<Customers />} />
        <Route path="customers/:id" element={<CustomerDetails />} />
        
        {/* Worker Management & Verification */}
        <Route path="workers" element={<Workers />} />
        <Route path="workers/:id" element={<WorkerDetails />} />
        <Route path="verifications" element={<VerificationRequests />} />
        <Route path="verification" element={<Navigate to="/admin/verifications" replace />} />
        <Route path="verifications/:id" element={<VerificationReview />} />
        
        {/* Service Management */}
        <Route path="service-categories" element={<ServiceCategories />} />
        <Route path="services" element={<Services />} />

        {/* Pricing Module (Screens 11 to 15) */}
        <Route path="pricing" element={<MarketPriceGuide />} />
        <Route path="pricing/new" element={<MarketPriceForm />} />
        <Route path="pricing/:id/edit" element={<MarketPriceForm />} />
        <Route path="pricing/visiting-charges" element={<VisitingCharges />} />
        <Route path="pricing/price-increase" element={<PriceIncreaseConfig />} />
        <Route path="pricing/tolerance" element={<PriceTolerance />} />

        {/* Operations Module (Screens 16 to 20) */}
        <Route path="jobs" element={<Jobs />} />
        <Route path="jobs/:id" element={<JobDetails />} />
        <Route path="inspections" element={<InspectionRequests />} />
        <Route path="inspections/:id" element={<InspectionDetails />} />
        <Route path="inspection-reports" element={<InspectionReports />} />

        {/* Inspection Audit & Quotations (Screens 21 to 25) */}
        <Route path="inspection-reports/:id" element={<InspectionReportDetails />} />
        <Route path="price-assessments/:id" element={<PriceAssessment />} />
        <Route path="flagged-pricing" element={<FlaggedPricing />} />
        <Route path="inspection-conversions" element={<InspectionConversions />} />
        <Route path="quotations" element={<Quotations />} />

        {/* Finance Module (Screens 26 to 30) */}
        <Route path="payments" element={<PaymentsDashboard />} />
        <Route path="transactions" element={<Transactions />} />
        <Route path="payouts" element={<WorkerPayouts />} />
        <Route path="refunds" element={<Refunds />} />
        <Route path="revenue" element={<Revenue />} />

        {/* Placeholder routes for remaining sidebar items */}
        <Route path="complaints" element={<PlaceholderPage />} />
        <Route path="reviews" element={<PlaceholderPage />} />
        <Route path="notifications" element={<PlaceholderPage />} />
        <Route path="analytics" element={<PlaceholderPage />} />
        <Route path="reports" element={<PlaceholderPage />} />
        <Route path="audit-logs" element={<PlaceholderPage />} />
        <Route path="admins" element={<PlaceholderPage />} />
        <Route path="settings" element={<PlaceholderPage />} />

        {/* Catch-all sub-route fallback */}
        <Route path="*" element={<PlaceholderPage />} />
      </Route>

      {/* Global Fallback Redirect */}
      <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
    </Routes>
  );
}

