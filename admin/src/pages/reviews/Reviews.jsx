import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Star,
  Search,
  Filter,
  Eye,
  Flag,
  EyeOff,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  MessageSquare,
  User,
  HardHat,
  Tag,
  X,
  FileText,
  ShieldAlert,
} from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import ReviewRating from '../../components/common/ReviewRating';
import Modal from '../../components/common/Modal';
import ConfirmModal from '../../components/common/ConfirmModal';
import EmptyState from '../../components/common/EmptyState';
import { useToast } from '../../components/common/ToastContext';
import { REVIEWS_DATA, REVIEWS_SUMMARY_DATA } from '../../data/reviews';

export default function Reviews() {
  const navigate = useNavigate();
  const { addToast } = useToast();

  const [reviews, setReviews] = useState(REVIEWS_DATA);

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [ratingFilter, setRatingFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All');

  // Selected Review Drawer/Modal
  const [selectedReview, setSelectedReview] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Confirmation Modal State (Hide / Restore / Flag)
  const [confirmModal, setConfirmModal] = useState({
    open: false,
    type: 'hide', // hide | restore | flag
    review: null,
    flagReason: 'Abusive Language',
  });

  // Summary Metrics
  const metrics = useMemo(() => {
    const total = reviews.length;
    const avg = (reviews.reduce((acc, r) => acc + r.rating, 0) / total).toFixed(1);
    const fiveStar = reviews.filter((r) => r.rating === 5).length;
    const low = reviews.filter((r) => r.rating <= 2).length;
    const flagged = reviews.filter((r) => r.status === 'Flagged').length;

    return { total, avg, fiveStar, low, flagged };
  }, [reviews]);

  // Filtered List
  const filteredReviews = useMemo(() => {
    return reviews.filter((r) => {
      // Search
      const query = searchQuery.toLowerCase().trim();
      if (query) {
        const matchesId = r.id.toLowerCase().includes(query);
        const matchesCust = r.customerName.toLowerCase().includes(query);
        const matchesWorker = r.workerName.toLowerCase().includes(query);
        const matchesService = r.service.toLowerCase().includes(query);
        const matchesJob = r.jobId.toLowerCase().includes(query);
        const matchesText = r.reviewText.toLowerCase().includes(query);

        if (!matchesId && !matchesCust && !matchesWorker && !matchesService && !matchesJob && !matchesText) {
          return false;
        }
      }

      // Rating Filter
      if (ratingFilter !== 'All') {
        const stars = parseInt(ratingFilter, 10);
        if (Math.floor(r.rating) !== stars) return false;
      }

      // Status Filter
      if (statusFilter !== 'All' && r.status !== statusFilter) return false;

      // Category Filter
      if (categoryFilter !== 'All' && r.category !== categoryFilter) return false;

      return true;
    });
  }, [reviews, searchQuery, ratingFilter, statusFilter, categoryFilter]);

  const handleOpenDrawer = (review) => {
    setSelectedReview(review);
    setDrawerOpen(true);
  };

  const handlePromptHide = (review) => {
    setConfirmModal({
      open: true,
      type: 'hide',
      review,
      flagReason: review.flagReason || 'Abusive Language',
    });
  };

  const handlePromptRestore = (review) => {
    setConfirmModal({
      open: true,
      type: 'restore',
      review,
      flagReason: '',
    });
  };

  const handlePromptFlag = (review) => {
    setConfirmModal({
      open: true,
      type: 'flag',
      review,
      flagReason: 'Personal Information',
    });
  };

  const handleExecuteAction = () => {
    const { type, review, flagReason } = confirmModal;
    if (!review) return;

    setReviews((prev) =>
      prev.map((r) => {
        if (r.id === review.id) {
          if (type === 'hide') {
            return { ...r, status: 'Hidden', flagReason };
          }
          if (type === 'restore') {
            return { ...r, status: 'Published', flagReason: null };
          }
          if (type === 'flag') {
            return { ...r, status: 'Flagged', flagReason };
          }
        }
        return r;
      })
    );

    addToast({
      title: 'Review Moderated',
      message: `Review ${review.id} status updated to ${
        type === 'hide' ? 'Hidden' : type === 'restore' ? 'Published' : 'Flagged'
      }. Original user text preserved untouched.`,
      type: 'success',
    });

    if (selectedReview && selectedReview.id === review.id) {
      setSelectedReview((prev) => ({
        ...prev,
        status: type === 'hide' ? 'Hidden' : type === 'restore' ? 'Published' : 'Flagged',
        flagReason: type === 'hide' || type === 'flag' ? flagReason : null,
      }));
    }

    setConfirmModal({ open: false, type: 'hide', review: null, flagReason: '' });
  };

  return (
    <PageContainer
      title="Reviews Management"
      subtitle="Monitor customer feedback, ratings breakdown, and moderate inappropriate service reviews."
    >
      <div className="space-y-6">
        {/* SUMMARY CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard
            title="Total Reviews"
            value={REVIEWS_SUMMARY_DATA.totalReviews}
            subtitle="Platform lifetime"
            icon={MessageSquare}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Average Rating"
            value={`${REVIEWS_SUMMARY_DATA.averageRating} ★`}
            subtitle="Customer satisfaction"
            icon={Star}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
          <StatCard
            title="5-Star Reviews"
            value={REVIEWS_SUMMARY_DATA.fiveStarReviews}
            subtitle="73% of total"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Low Ratings (1–2★)"
            value={REVIEWS_SUMMARY_DATA.lowRatings}
            subtitle="Requires attention"
            icon={AlertTriangle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#DC2626]"
          />
          <StatCard
            title="Flagged Reviews"
            value={REVIEWS_SUMMARY_DATA.flaggedReviews}
            subtitle="Moderation queue"
            icon={Flag}
            iconBg="bg-[#FFF7ED]"
            iconColor="text-[#EA580C]"
          />
        </div>

        {/* RATING DISTRIBUTION BREAKDOWN */}
        <div className="bg-white rounded-2xl p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
          <h3 className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider">
            Overall Rating Distribution
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {REVIEWS_SUMMARY_DATA.ratingDistribution.map((item) => (
              <div
                key={item.stars}
                onClick={() => setRatingFilter(item.stars.toString())}
                className="cursor-pointer p-3 bg-[#F8FAFC] rounded-xl border border-[#E2E8F0] hover:border-[#2563EB] transition-all space-y-2 group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1 font-bold text-xs text-[#0F172A]">
                    <span>{item.stars}</span>
                    <Star className="w-3.5 h-3.5 fill-[#F59E0B] text-[#F59E0B]" />
                  </div>
                  <span className="text-[11px] font-extrabold text-[#64748B] group-hover:text-[#2563EB]">
                    {item.count} ({item.percentage}%)
                  </span>
                </div>
                {/* Progress Bar */}
                <div className="w-full h-2 bg-[#E2E8F0] rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.stars >= 4
                        ? 'bg-[#16A34A]'
                        : item.stars === 3
                        ? 'bg-[#F59E0B]'
                        : 'bg-[#EF4444]'
                    }`}
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SEARCH & FILTERS CONTROLS */}
        <div className="bg-white rounded-2xl p-4 sm:p-5 border border-[#E2E8F0] shadow-2xs space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center gap-4">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search customer, worker, review content or job ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-xs font-medium bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB]"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#0F172A]"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Filter Controls */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <select
                  value={ratingFilter}
                  onChange={(e) => setRatingFilter(e.target.value)}
                  className="w-full px-3 py-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
                >
                  <option value="All">All Ratings</option>
                  <option value="5">5 Stars</option>
                  <option value="4">4 Stars</option>
                  <option value="3">3 Stars</option>
                  <option value="2">2 Stars</option>
                  <option value="1">1 Star</option>
                </select>
              </div>

              <div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full px-3 py-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
                >
                  <option value="All">All Statuses</option>
                  <option value="Published">Published</option>
                  <option value="Flagged">Flagged</option>
                  <option value="Hidden">Hidden</option>
                  <option value="Under Review">Under Review</option>
                </select>
              </div>

              <div>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="w-full px-3 py-2.5 text-xs font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl focus:outline-none focus:border-[#2563EB]"
                >
                  <option value="All">All Categories</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Plumbing">Plumbing</option>
                  <option value="AC Repair">AC Repair</option>
                  <option value="Carpentry">Carpentry</option>
                  <option value="Painting">Painting</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* REVIEWS TABLE */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] shadow-2xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[1000px]">
              <thead>
                <tr className="bg-[#F8FAFC] border-b border-[#E2E8F0] text-[11px] font-extrabold text-[#64748B] uppercase tracking-wider">
                  <th className="py-3.5 px-4">Review ID</th>
                  <th className="py-3.5 px-4">Customer</th>
                  <th className="py-3.5 px-4">Worker</th>
                  <th className="py-3.5 px-4">Service / Job</th>
                  <th className="py-3.5 px-4">Rating</th>
                  <th className="py-3.5 px-4">Review Text</th>
                  <th className="py-3.5 px-4">Date</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] text-xs">
                {filteredReviews.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-12 text-center">
                      <EmptyState
                        icon={Star}
                        title="No reviews match filter"
                        description="Try adjusting your rating or status filters."
                      />
                    </td>
                  </tr>
                ) : (
                  filteredReviews.map((r) => {
                    const isLowRating = r.rating <= 2.0;
                    return (
                      <tr
                        key={r.id}
                        className={`transition-colors ${
                          isLowRating
                            ? 'bg-[#FEF2F2]/30 hover:bg-[#FEF2F2]/60'
                            : 'hover:bg-[#F8FAFC]'
                        }`}
                      >
                        {/* ID */}
                        <td className="py-4 px-4 font-mono font-bold text-[#0F172A]">
                          {r.id}
                        </td>

                        {/* Customer */}
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-2">
                            <img
                              src={r.customerAvatar}
                              alt={r.customerName}
                              className="w-7 h-7 rounded-full object-cover border border-[#E2E8F0]"
                            />
                            <span className="font-bold text-[#0F172A]">
                              {r.customerName}
                            </span>
                          </div>
                        </td>

                        {/* Worker */}
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-2">
                            <img
                              src={r.workerAvatar}
                              alt={r.workerName}
                              className="w-7 h-7 rounded-full object-cover border border-[#E2E8F0]"
                            />
                            <div className="flex flex-col">
                              <span className="font-bold text-[#0F172A]">
                                {r.workerName}
                              </span>
                              <span className="text-[10px] text-[#64748B]">
                                {r.workerProfession}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Service / Job */}
                        <td className="py-4 px-4">
                          <div className="flex flex-col gap-0.5">
                            <span className="font-semibold text-[#334155]">
                              {r.service}
                            </span>
                            <span className="font-mono text-[10px] text-[#2563EB]">
                              {r.jobId}
                            </span>
                          </div>
                        </td>

                        {/* Rating */}
                        <td className="py-4 px-4">
                          <ReviewRating rating={r.rating} />
                        </td>

                        {/* Excerpt Text */}
                        <td className="py-4 px-4 max-w-xs">
                          <p className="line-clamp-2 text-[#334155] leading-relaxed">
                            "{r.reviewText}"
                          </p>
                          {r.workerResponse && (
                            <span className="text-[10px] text-[#2563EB] font-bold block mt-1">
                              ✓ Worker Responded
                            </span>
                          )}
                        </td>

                        {/* Date */}
                        <td className="py-4 px-4 text-[#64748B] font-medium">
                          {r.createdAt.split(' ')[0]}
                        </td>

                        {/* Status */}
                        <td className="py-4 px-4">
                          {r.status === 'Published' && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#DCFCE7] text-[#16A34A] text-[11px] font-bold">
                              Published
                            </span>
                          )}
                          {r.status === 'Flagged' && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#FEF3C7] text-[#D97706] text-[11px] font-bold">
                              Flagged ({r.flagReason})
                            </span>
                          )}
                          {r.status === 'Hidden' && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#F1F5F9] text-[#64748B] text-[11px] font-bold">
                              Hidden
                            </span>
                          )}
                          {r.status === 'Under Review' && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#EFF6FF] text-[#2563EB] text-[11px] font-bold">
                              Under Review
                            </span>
                          )}
                        </td>

                        {/* Actions */}
                        <td className="py-4 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleOpenDrawer(r)}
                              className="p-1.5 text-[#2563EB] hover:bg-[#EFF6FF] rounded-lg transition-colors"
                              title="View Full Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>

                            {r.status === 'Published' && (
                              <button
                                onClick={() => handlePromptFlag(r)}
                                className="p-1.5 text-[#D97706] hover:bg-[#FEF3C7] rounded-lg transition-colors"
                                title="Flag Review"
                              >
                                <Flag className="w-4 h-4" />
                              </button>
                            )}

                            {r.status !== 'Hidden' ? (
                              <button
                                onClick={() => handlePromptHide(r)}
                                className="p-1.5 text-[#DC2626] hover:bg-[#FEE2E2] rounded-lg transition-colors"
                                title="Hide Review"
                              >
                                <EyeOff className="w-4 h-4" />
                              </button>
                            ) : (
                              <button
                                onClick={() => handlePromptRestore(r)}
                                className="p-1.5 text-[#16A34A] hover:bg-[#DCFCE7] rounded-lg transition-colors"
                                title="Restore Review"
                              >
                                <RotateCcw className="w-4 h-4" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* REVIEW DETAILS DRAWER / MODAL */}
      <Modal
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={`Review Moderation Details — ${selectedReview?.id}`}
      >
        {selectedReview && (
          <div className="space-y-5 py-2">
            {/* Header info */}
            <div className="flex items-center justify-between bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0]">
              <ReviewRating rating={selectedReview.rating} size="md" />
              <div className="flex items-center gap-2">
                <span className="text-xs text-[#64748B] font-bold">
                  Status:
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-white border border-[#E2E8F0] text-[#0F172A]">
                  {selectedReview.status}
                </span>
              </div>
            </div>

            {/* Original Customer Review Text */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-[#64748B] uppercase tracking-wider">
                  Original Customer Written Content
                </span>
                <span className="text-[10px] text-[#94A3B8] italic font-semibold">
                  (Strictly read-only — admin editing disabled)
                </span>
              </div>
              <p className="text-xs text-[#0F172A] bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0] leading-relaxed font-medium">
                "{selectedReview.reviewText}"
              </p>
            </div>

            {/* Worker Response if available */}
            {selectedReview.workerResponse && (
              <div className="space-y-1.5 bg-[#EFF6FF] p-4 rounded-xl border border-[#BFDBFE]">
                <div className="flex items-center justify-between text-xs font-bold text-[#2563EB]">
                  <span>Worker Public Response</span>
                  <span>{selectedReview.workerResponseDate}</span>
                </div>
                <p className="text-xs text-[#1E3A8A] italic">
                  "{selectedReview.workerResponse}"
                </p>
              </div>
            )}

            {/* Metadata Links */}
            <div className="grid grid-cols-2 gap-3 pt-2 text-xs border-t border-[#F1F5F9]">
              <div className="space-y-1">
                <span className="text-[#64748B] font-semibold block">Customer</span>
                <button
                  onClick={() => navigate(`/admin/customers/${selectedReview.customerId}`)}
                  className="font-bold text-[#2563EB] hover:underline flex items-center gap-1"
                >
                  {selectedReview.customerName} ({selectedReview.customerId})
                </button>
              </div>
              <div className="space-y-1">
                <span className="text-[#64748B] font-semibold block">Professional</span>
                <button
                  onClick={() => navigate(`/admin/workers/${selectedReview.workerId}`)}
                  className="font-bold text-[#2563EB] hover:underline flex items-center gap-1"
                >
                  {selectedReview.workerName} ({selectedReview.workerId})
                </button>
              </div>
            </div>

            {/* Actions Bar */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-4 border-t border-[#E2E8F0]">
              <button
                onClick={() => navigate(`/admin/jobs/${selectedReview.jobId}`)}
                className="px-3.5 py-2 text-xs font-bold text-[#2563EB] bg-[#EFF6FF] hover:bg-[#DBEAFE] rounded-xl transition-colors flex items-center gap-1"
              >
                Inspect Related Job {selectedReview.jobId}
              </button>

              <div className="flex items-center gap-2">
                {selectedReview.status !== 'Hidden' ? (
                  <button
                    onClick={() => handlePromptHide(selectedReview)}
                    className="px-4 py-2 text-xs font-bold text-white bg-[#DC2626] hover:bg-[#B91C1C] rounded-xl transition-colors shadow-2xs"
                  >
                    Hide Review
                  </button>
                ) : (
                  <button
                    onClick={() => handlePromptRestore(selectedReview)}
                    className="px-4 py-2 text-xs font-bold text-white bg-[#16A34A] hover:bg-[#15803D] rounded-xl transition-colors shadow-2xs"
                  >
                    Restore to Published
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* CONFIRMATION MODAL FOR HIDE / RESTORE / FLAG */}
      <Modal
        isOpen={confirmModal.open}
        onClose={() => setConfirmModal((prev) => ({ ...prev, open: false }))}
        title={
          confirmModal.type === 'hide'
            ? 'Hide Customer Review?'
            : confirmModal.type === 'restore'
            ? 'Restore Review to Public?'
            : 'Flag Review for Moderation?'
        }
      >
        <div className="space-y-4 py-2 text-xs">
          <p className="text-[#475569] leading-relaxed">
            {confirmModal.type === 'hide'
              ? `Are you sure you want to hide review ${confirmModal.review?.id}? It will no longer be visible on worker profile.`
              : confirmModal.type === 'restore'
              ? `Restore review ${confirmModal.review?.id} back to public view?`
              : `Flag review ${confirmModal.review?.id} for policy violation review?`}
          </p>

          {(confirmModal.type === 'hide' || confirmModal.type === 'flag') && (
            <div>
              <label className="block font-bold text-[#0F172A] mb-1">
                Moderation Reason
              </label>
              <select
                value={confirmModal.flagReason}
                onChange={(e) =>
                  setConfirmModal((prev) => ({ ...prev, flagReason: e.target.value }))
                }
                className="w-full p-2.5 font-semibold bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl"
              >
                <option value="Abusive Language">Abusive Language</option>
                <option value="Personal Information">Personal Information</option>
                <option value="Spam">Spam</option>
                <option value="Irrelevant Content">Irrelevant Content</option>
                <option value="Threatening Content">Threatening Content</option>
                <option value="Fake Review Suspected">Fake Review Suspected</option>
                <option value="Other">Other</option>
              </select>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E2E8F0]">
            <button
              onClick={() => setConfirmModal((prev) => ({ ...prev, open: false }))}
              className="px-4 py-2 font-bold text-[#64748B] hover:text-[#0F172A] bg-[#F1F5F9] rounded-xl"
            >
              Cancel
            </button>
            <button
              onClick={handleExecuteAction}
              className={`px-4 py-2 font-bold text-white rounded-xl shadow-sm ${
                confirmModal.type === 'hide'
                  ? 'bg-[#DC2626] hover:bg-[#B91C1C]'
                  : confirmModal.type === 'restore'
                  ? 'bg-[#16A34A] hover:bg-[#15803D]'
                  : 'bg-[#D97706] hover:bg-[#B45309]'
              }`}
            >
              Confirm
            </button>
          </div>
        </div>
      </Modal>
    </PageContainer>
  );
}
