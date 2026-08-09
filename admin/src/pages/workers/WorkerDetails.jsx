import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  HardHat,
  Phone,
  Mail,
  MapPin,
  Star,
  BadgeCheck,
  UserMinus,
  Award,
  Shield,
  Plus,
  Save,
  X,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatusBadge from '../../components/common/StatusBadge';
import ConfirmModal from '../../components/common/ConfirmModal';
import { adminService } from '../../services/adminService';

const DEFAULT_CATEGORY_OPTIONS = [
  { slug: 'electrical', name: 'Electrical' },
  { slug: 'plumbing', name: 'Plumbing' },
  { slug: 'cleaning', name: 'Cleaning' },
  { slug: 'painting', name: 'Painting' },
  { slug: 'carpentry', name: 'Carpentry' },
  { slug: 'appliance-repair', name: 'Appliance Repair' },
  { slug: 'handyman', name: 'Handyman' },
  { slug: 'ac-repair', name: 'AC Repair' },
];

export default function WorkerDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [worker, setWorker] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [editableSkills, setEditableSkills] = useState([]);
  const [editableRadius, setEditableRadius] = useState(10.0);
  const [availableCategories, setAvailableCategories] = useState(DEFAULT_CATEGORY_OPTIONS);
  const [selectedSkillToAdd, setSelectedSkillToAdd] = useState('');

  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(null);

  const [internalNotes, setInternalNotes] = useState([
    'Worker profile loaded from database.',
  ]);
  const [newNote, setNewNote] = useState('');
  const [modalConfig, setModalConfig] = useState({ isOpen: false });

  // Load worker details and canonical categories from API
  useEffect(() => {
    async function loadWorkerData() {
      setIsLoading(true);
      setLoadError(null);
      try {
        const [workerData, catData] = await Promise.all([
          adminService.getWorkerDetails(id),
          adminService.getCategories(),
        ]);

        if (workerData) {
          setWorker(workerData);
          setEditableSkills(workerData.skills || []);
          setEditableRadius(workerData.working_radius_km || 10.0);
        } else {
          setLoadError(`Worker with ID '${id}' was not found.`);
        }

        if (Array.isArray(catData) && catData.length > 0) {
          const parsedCats = catData
            .filter((c) => c && c.slug)
            .map((c) => ({
              slug: c.slug.toLowerCase(),
              name: c.name || c.slug,
            }));
          if (parsedCats.length > 0) {
            setAvailableCategories(parsedCats);
          }
        }
      } catch (err) {
        console.error('Failed to load worker details:', err);
        setLoadError(err.message || 'Failed to load worker details from server');
      } finally {
        setIsLoading(false);
      }
    }

    loadWorkerData();
  }, [id]);

  const handleAddSkill = () => {
    if (!selectedSkillToAdd) return;
    const cleanSlug = selectedSkillToAdd.trim().toLowerCase();
    if (!editableSkills.includes(cleanSlug)) {
      setEditableSkills([...editableSkills, cleanSlug]);
    }
    setSelectedSkillToAdd('');
  };

  const handleRemoveSkill = (skillToRemove) => {
    setEditableSkills(editableSkills.filter((s) => s !== skillToRemove));
  };

  const handleSaveChanges = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveError(null);
    setSaveSuccess(null);

    try {
      const updated = await adminService.updateWorkerProfile(id, {
        skills: editableSkills,
        working_radius_km: parseFloat(editableRadius) || 10.0,
      });

      if (updated) {
        setWorker((prev) => ({
          ...prev,
          skills: updated.skills,
          working_radius_km: updated.working_radius_km,
        }));
        setSaveSuccess('Worker skills and service radius updated successfully!');
      }
    } catch (err) {
      console.error('Save worker profile error:', err);
      setSaveError(err.message || 'Failed to save worker profile changes.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateAccountStatus = (newStatus) => {
    setWorker((prev) => (prev ? { ...prev, is_active: newStatus === 'Active' } : prev));
  };

  const handleAddNote = (e) => {
    e.preventDefault();
    if (newNote.trim()) {
      setInternalNotes([...internalNotes, newNote.trim()]);
      setNewNote('');
    }
  };

  if (isLoading) {
    return (
      <PageContainer>
        <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
          <Loader2 className="w-8 h-8 text-[#2563EB] animate-spin" />
          <p className="text-xs font-bold text-[#64748B]">Loading worker profile from server...</p>
        </div>
      </PageContainer>
    );
  }

  if (loadError || !worker) {
    return (
      <PageContainer>
        <div className="space-y-6">
          <button
            onClick={() => navigate('/admin/workers')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Workers</span>
          </button>
          <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-red-500 mx-auto" />
            <h2 className="text-base font-extrabold text-red-900">Worker Not Found</h2>
            <p className="text-xs font-medium text-red-600">{loadError || 'Unable to retrieve worker details from the database.'}</p>
          </div>
        </div>
      </PageContainer>
    );
  }

  const unselectedCategories = availableCategories.filter(
    (c) => !editableSkills.includes(c.slug)
  );

  return (
    <PageContainer>
      <div className="space-y-6">
        {/* ── Top Header Navigation Bar ────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <button
            onClick={() => navigate('/admin/workers')}
            className="inline-flex items-center gap-2 text-xs font-extrabold text-[#64748B] hover:text-[#0F172A] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Workers</span>
          </button>

          <div className="flex items-center gap-3">
            <Link
              to={`/admin/verifications`}
              className="px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-extrabold rounded-xl shadow-xs transition-colors flex items-center gap-1.5"
            >
              <BadgeCheck className="w-4 h-4" />
              <span>Review Verification</span>
            </Link>

            {!worker.is_active ? (
              <button
                onClick={() => handleUpdateAccountStatus('Active')}
                className="px-4 py-2 bg-[#DCFCE7] hover:bg-[#BBF7D0] text-[#16A34A] text-xs font-extrabold rounded-xl border border-[#BBF7D0] transition-colors"
              >
                Unsuspend Worker
              </button>
            ) : (
              <button
                onClick={() =>
                  setModalConfig({
                    isOpen: true,
                    title: `Suspend ${worker.full_name}?`,
                    message:
                      'Suspend worker account temporarily from receiving new job dispatches.',
                    confirmText: 'Suspend Worker',
                    confirmVariant: 'warning',
                    onConfirm: () => handleUpdateAccountStatus('Suspended'),
                  })
                }
                className="px-4 py-2 bg-[#FEF3C7] hover:bg-[#FDE68A] text-[#D97706] text-xs font-extrabold rounded-xl border border-[#FDE68A] transition-colors flex items-center gap-1.5"
              >
                <UserMinus className="w-4 h-4" />
                <span>Suspend Worker</span>
              </button>
            )}
          </div>
        </div>

        {/* Feedback Alert Banners */}
        {saveSuccess && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between text-xs text-emerald-800 font-bold">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>{saveSuccess}</span>
            </div>
            <button onClick={() => setSaveSuccess(null)} className="text-emerald-500 hover:text-emerald-700">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {saveError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between text-xs text-red-800 font-bold">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span>{saveError}</span>
            </div>
            <button onClick={() => setSaveError(null)} className="text-red-500 hover:text-red-700">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* ── Top Profile Banner Card ───────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-[#E2E8F0] p-6 shadow-xs flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center font-black text-2xl ring-4 ring-[#F8FAFC] border border-[#E2E8F0]">
              {worker.full_name ? worker.full_name.charAt(0).toUpperCase() : 'W'}
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 flex-wrap">
                <h1 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
                  {worker.full_name}
                </h1>
                <span className="px-2.5 py-0.5 rounded-md bg-[#EFF6FF] text-[#2563EB] text-xs font-extrabold">
                  {editableSkills.length > 0 ? editableSkills[0] : 'No Skills Assigned'}
                </span>
              </div>

              {/* Status Badges */}
              <div className="flex items-center gap-2 flex-wrap pt-1">
                <div className="flex items-center gap-1 text-[11px] font-bold text-[#64748B]">
                  <span>Verification:</span>
                  <StatusBadge
                    status={worker.is_verified ? 'Verified' : 'Unverified'}
                    type="verification"
                  />
                </div>

                <div className="h-3 w-px bg-[#E2E8F0]" />

                <div className="flex items-center gap-1 text-[11px] font-bold text-[#64748B]">
                  <span>Account:</span>
                  <StatusBadge status={worker.is_active ? 'Active' : 'Suspended'} type="account" />
                </div>

                <div className="h-3 w-px bg-[#E2E8F0]" />

                <div className="flex items-center gap-1 text-[11px] font-bold text-[#64748B]">
                  <span>Availability:</span>
                  <StatusBadge
                    status={worker.availability || 'Available'}
                    type="availability"
                  />
                </div>
              </div>

              <p className="text-xs text-[#64748B] font-semibold pt-1">
                Worker ID: <strong className="text-[#0F172A]">{worker.id}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 border-t lg:border-t-0 lg:border-l border-[#F1F5F9] pt-4 lg:pt-0 lg:pl-6 text-xs">
            <div>
              <p className="text-[#64748B] font-bold">Rating</p>
              <p className="text-xl font-black text-[#0F172A] mt-0.5 flex items-center gap-1">
                <Star className="w-5 h-5 fill-[#EAB308] text-[#EAB308]" />
                <span>{worker.rating || 0.0}</span>
              </p>
            </div>
            <div>
              <p className="text-[#64748B] font-bold">Reviews</p>
              <p className="text-xl font-black text-[#16A34A] mt-0.5">
                {worker.review_count || 0}
              </p>
            </div>
          </div>
        </div>

        {/* ── Admin Management Panel: Edit Skills & Service Radius ───── */}
        <form onSubmit={handleSaveChanges} className="bg-white rounded-3xl border border-[#2563EB]/30 p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-4">
            <div className="flex items-center gap-2">
              <HardHat className="w-5 h-5 text-[#2563EB]" />
              <div>
                <h2 className="text-base font-extrabold text-[#0F172A]">Worker Skill & Radius Management</h2>
                <p className="text-xs text-[#64748B] font-medium">Update canonical category skills and working radius for marketplace eligibility.</p>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSaving}
              className="px-5 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:bg-[#94A3B8] text-white text-xs font-black rounded-xl shadow-sm transition-all flex items-center gap-2"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              <span>{isSaving ? 'Saving Changes...' : 'Save Profile Changes'}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Skills Multi-Select Management */}
            <div className="space-y-3">
              <label className="block text-xs font-black text-[#0F172A] uppercase tracking-wider">
                Canonical Category Skills ({editableSkills.length})
              </label>

              {editableSkills.length === 0 ? (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 font-medium">
                  ⚠️ No skills assigned. Worker will be ineligible for all skill-matched marketplace bookings.
                </div>
              ) : (
                <div className="flex flex-wrap gap-2 p-3 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl min-h-[50px]">
                  {editableSkills.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#EFF6FF] text-[#2563EB] font-black text-xs rounded-lg border border-[#BFDBFE]"
                    >
                      <span>{skill}</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveSkill(skill)}
                        className="text-[#2563EB] hover:text-red-600 transition-colors"
                        title="Remove skill"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </span>
                  ))}
                </div>
              )}

              {/* Add Skill Controls */}
              <div className="flex items-center gap-2">
                <select
                  value={selectedSkillToAdd}
                  onChange={(e) => setSelectedSkillToAdd(e.target.value)}
                  className="flex-1 px-3 py-2 bg-white border border-[#E2E8F0] rounded-xl text-xs font-bold text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                >
                  <option value="">Select category skill to add...</option>
                  {unselectedCategories.map((c) => (
                    <option key={c.slug} value={c.slug}>
                      {c.name} ({c.slug})
                    </option>
                  ))}
                </select>

                <button
                  type="button"
                  onClick={handleAddSkill}
                  disabled={!selectedSkillToAdd}
                  className="px-3.5 py-2 bg-[#F1F5F9] hover:bg-[#E2E8F0] disabled:opacity-50 text-[#0F172A] text-xs font-extrabold rounded-xl transition-colors flex items-center gap-1 shrink-0"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Skill</span>
                </button>
              </div>

              {editableSkills.length > 0 && (
                <button
                  type="button"
                  onClick={() => setEditableSkills([])}
                  className="text-[11px] font-bold text-red-500 hover:text-red-700 underline pt-1"
                >
                  Clear All Skills
                </button>
              )}
            </div>

            {/* Service Radius Management */}
            <div className="space-y-3">
              <label className="block text-xs font-black text-[#0F172A] uppercase tracking-wider">
                Service Working Radius (KM)
              </label>

              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="0.1"
                  max="100.0"
                  step="0.5"
                  value={editableRadius}
                  onChange={(e) => setEditableRadius(e.target.value)}
                  className="w-32 px-4 py-2 bg-white border border-[#E2E8F0] rounded-xl text-sm font-black text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
                />
                <span className="text-xs font-extrabold text-[#64748B]">Kilometers</span>
              </div>

              <p className="text-[11px] text-[#64748B] font-medium leading-relaxed">
                Determines the maximum distance ($geoWithin) within which this worker will see and receive marketplace booking dispatches. Must be between 0.1 and 100 km.
              </p>
            </div>
          </div>
        </form>

        {/* ── Info Grid (Personal Info & Bio) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Personal Info */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center gap-2 border-b border-[#F1F5F9] pb-3">
              <HardHat className="w-4 h-4 text-[#2563EB]" />
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Personal & Identity Details
              </h3>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Full Name</span>
                <span className="font-bold text-[#0F172A]">{worker.full_name}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Phone</span>
                <span className="font-bold text-[#0F172A]">{worker.phone}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Email</span>
                <span className="font-bold text-[#0F172A]">{worker.email}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Profile Completed</span>
                <span className="font-bold text-[#16A34A]">{worker.profile_completed ? 'Yes (>= 70%)' : 'No'}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-[#64748B] font-medium">Experience Years</span>
                <span className="font-bold text-[#0F172A]">{worker.experience_years || 0} Years</span>
              </div>
            </div>
          </div>

          {/* Verification Summary */}
          <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-3">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#2563EB]" />
                <h3 className="text-base font-extrabold text-[#0F172A]">
                  Verification & Trust Status
                </h3>
              </div>
              <StatusBadge
                status={worker.is_verified ? 'Verified' : 'Unverified'}
                type="verification"
              />
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">Verification Status</span>
                <span className="font-bold text-[#0F172A]">{worker.is_verified ? 'Approved & Verified' : 'Pending / Unverified'}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-[#F8FAFC]">
                <span className="text-[#64748B] font-medium">GPS Location Updated</span>
                <span className="font-bold text-[#0F172A]">{worker.current_location_updated_at ? new Date(worker.current_location_updated_at).toLocaleString() : 'Not set'}</span>
              </div>
            </div>

            <Link
              to={`/admin/verifications`}
              className="w-full py-2.5 bg-[#EFF6FF] hover:bg-[#DBEAFE] text-[#2563EB] text-xs font-bold rounded-xl flex items-center justify-center gap-1.5 transition-colors"
            >
              <BadgeCheck className="w-4 h-4" />
              <span>Review Verification Queue</span>
            </Link>
          </div>
        </div>

        {/* ── Internal Administrative Notes Card ────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Administrative Notes
            </h3>
            <span className="px-2.5 py-0.5 rounded-md bg-[#FEF3C7] text-[#D97706] text-[10px] font-bold">
              Visible to admins only
            </span>
          </div>

          <div className="space-y-2 text-xs">
            {internalNotes.map((note, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] text-[#0F172A] font-medium"
              >
                • {note}
              </div>
            ))}
          </div>

          <form onSubmit={handleAddNote} className="flex gap-2">
            <input
              type="text"
              value={newNote}
              onChange={(e) => setNewNote(e.target.value)}
              placeholder="Add internal note for this worker..."
              className="flex-1 px-4 py-2 bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl text-xs text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-[#2563EB] text-white text-xs font-bold rounded-xl hover:bg-[#1D4ED8] transition-colors flex items-center gap-1 shrink-0"
            >
              <Plus className="w-4 h-4" />
              <span>Add Note</span>
            </button>
          </form>
        </div>
      </div>

      {/* Confirmation Modal */}
      <ConfirmModal
        isOpen={modalConfig.isOpen}
        title={modalConfig.title}
        message={modalConfig.message}
        confirmText={modalConfig.confirmText}
        confirmVariant={modalConfig.confirmVariant}
        onConfirm={modalConfig.onConfirm || (() => {})}
        onClose={() => setModalConfig({ isOpen: false })}
      />
    </PageContainer>
  );
}
