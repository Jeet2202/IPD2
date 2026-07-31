import React, { useState } from 'react';
import {
  ShieldCheck,
  UserPlus,
  Users,
  CheckCircle2,
  XCircle,
  Shield,
  Lock,
  Mail,
  Building,
  Edit2,
  Trash2,
  Eye,
  Check,
  X,
  Sparkles,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import StatCard from '../../components/cards/StatCard';
import RoleBadge from '../../components/common/RoleBadge';
import Modal from '../../components/common/Modal';
import { useToast } from '../../components/common/ToastContext';
import {
  ADMIN_SUMMARY,
  ADMIN_ROLES,
  ADMIN_DEPARTMENTS,
  ROLE_PERMISSIONS_MATRIX,
  ADMIN_USERS_LIST,
} from '../../data/admins';

export default function AdminUsers() {
  const { addToast } = useToast();
  const [adminsList, setAdminsList] = useState(ADMIN_USERS_LIST);
  const [selectedRoleTab, setSelectedRoleTab] = useState('Super Admin');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingAdmin, setEditingAdmin] = useState(null);

  // New Admin Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'Operations Admin',
    department: 'Operations & Field',
    status: 'Active',
  });

  const handleOpenAddModal = () => {
    setEditingAdmin(null);
    setFormData({
      name: '',
      email: '',
      role: 'Operations Admin',
      department: 'Operations & Field',
      status: 'Active',
    });
    setIsAddModalOpen(true);
  };

  const handleSaveAdmin = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email) {
      addToast({
        title: 'Validation Error',
        message: 'Name and Email address are required fields.',
        type: 'error',
      });
      return;
    }

    if (editingAdmin) {
      setAdminsList(
        adminsList.map((a) =>
          a.id === editingAdmin.id ? { ...a, ...formData } : a
        )
      );
      addToast({
        title: 'Account Updated',
        message: `Admin user profile for ${formData.name} updated successfully.`,
        type: 'success',
      });
      setEditingAdmin(null);
    } else {
      const newAdmin = {
        id: `ADM-${Math.floor(100 + Math.random() * 900)}`,
        ...formData,
        lastLogin: 'Just now',
        avatar: `https://images.unsplash.com/photo-${1500000000000 + Math.floor(Math.random() * 100000)}?w=150`,
      };
      setAdminsList([newAdmin, ...adminsList]);
      addToast({
        title: 'Admin Created',
        message: `New admin account created for ${formData.name}.`,
        type: 'success',
      });
    }
    setIsAddModalOpen(false);
  };

  const handleToggleStatus = (id) => {
    let updatedAdminName = '';
    let newStatus = '';
    setAdminsList(
      adminsList.map((a) => {
        if (a.id === id) {
          updatedAdminName = a.name;
          newStatus = a.status === 'Active' ? 'Suspended' : 'Active';
          return { ...a, status: newStatus };
        }
        return a;
      })
    );
    addToast({
      title: `Account ${newStatus}`,
      message: `${updatedAdminName} account status is now ${newStatus}.`,
      type: newStatus === 'Active' ? 'success' : 'warning',
    });
  };

  const selectedRolePermissions = ROLE_PERMISSIONS_MATRIX.find(
    (r) => r.role === selectedRoleTab
  );

  return (
    <PageContainer
      title="Admin Users & Roles"
      subtitle="Manage internal admin team accounts, roles and system permission matrix."
      action={
        <button
          onClick={handleOpenAddModal}
          className="flex items-center gap-2 px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl transition-colors shadow-xs"
        >
          <UserPlus className="w-4 h-4" />
          <span>Add Admin User</span>
        </button>
      }
    >
      <div className="space-y-6">
        {/* ── SUMMARY CARDS ───────────────────────────────────────── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Admin Accounts"
            value={adminsList.length.toString()}
            description="Active platform operators"
            icon={ShieldCheck}
            iconBg="bg-[#EFF6FF]"
            iconColor="text-[#2563EB]"
          />
          <StatCard
            title="Active Admins"
            value={adminsList.filter((a) => a.status === 'Active').length.toString()}
            change="Operational"
            changeType="positive"
            description="Granted system access"
            icon={CheckCircle2}
            iconBg="bg-[#DCFCE7]"
            iconColor="text-[#16A34A]"
          />
          <StatCard
            title="Suspended Accounts"
            value={adminsList.filter((a) => a.status === 'Suspended').length.toString()}
            change="Access Revoked"
            changeType="negative"
            description="Temporarily disabled"
            icon={XCircle}
            iconBg="bg-[#FEE2E2]"
            iconColor="text-[#EF4444]"
          />
          <StatCard
            title="Super Admins"
            value={adminsList.filter((a) => a.role === 'Super Admin').length.toString()}
            description="Full root authority"
            icon={Shield}
            iconBg="bg-[#FEF3C7]"
            iconColor="text-[#D97706]"
          />
        </div>

        {/* ── PERMISSIONS MATRIX PREVIEW ──────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Role Permissions Matrix Preview
              </h3>
              <p className="text-xs text-[#64748B]">Visual access permissions per administrative role</p>
            </div>
          </div>

          {/* Role selector tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {ADMIN_ROLES.map((role) => (
              <button
                key={role}
                onClick={() => setSelectedRoleTab(role)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                  selectedRoleTab === role
                    ? 'bg-[#2563EB] text-white shadow-xs'
                    : 'bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#64748B] hover:text-[#0F172A] border border-[#E2E8F0]'
                }`}
              >
                {role}
              </button>
            ))}
          </div>

          {/* Permission Items Table */}
          {selectedRolePermissions && (
            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-[#0F172A] flex items-center gap-2">
                    <RoleBadge role={selectedRolePermissions.role} />
                  </h4>
                  <p className="text-xs text-[#64748B] mt-1">
                    {selectedRolePermissions.description}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-[#E2E8F0]">
                {Object.entries(selectedRolePermissions.permissions).map(
                  ([mod, allowed]) => (
                    <div
                      key={mod}
                      className={`p-2.5 rounded-lg border flex items-center justify-between ${
                        allowed
                          ? 'bg-[#DCFCE7]/60 border-[#BBF7D0] text-[#166534]'
                          : 'bg-[#F1F5F9] border-[#E2E8F0] text-[#94A3B8]'
                      }`}
                    >
                      <span className="text-xs font-bold capitalize">{mod}</span>
                      {allowed ? (
                        <span className="w-5 h-5 rounded-full bg-[#16A34A] text-white flex items-center justify-center shrink-0">
                          <Check className="w-3.5 h-3.5" />
                        </span>
                      ) : (
                        <span className="w-5 h-5 rounded-full bg-[#CBD5E1] text-[#64748B] flex items-center justify-center shrink-0">
                          <X className="w-3.5 h-3.5" />
                        </span>
                      )}
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>

        {/* ── ADMIN USERS TABLE ───────────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-extrabold text-[#0F172A]">
              Registered Admin Team ({adminsList.length})
            </h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#F1F5F9] text-[#94A3B8] font-bold uppercase tracking-wider">
                  <th className="pb-3 px-3">Admin User</th>
                  <th className="pb-3 px-3">Email Address</th>
                  <th className="pb-3 px-3">Role</th>
                  <th className="pb-3 px-3">Department</th>
                  <th className="pb-3 px-3">Status</th>
                  <th className="pb-3 px-3">Last Active Login</th>
                  <th className="pb-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {adminsList.map((admin) => (
                  <tr key={admin.id} className="hover:bg-[#F8FAFC] transition-colors">
                    <td className="py-3 px-3 font-bold text-[#0F172A]">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-[#2563EB] text-white font-black flex items-center justify-center text-xs shrink-0 shadow-xs">
                          {admin.name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-bold text-[#0F172A]">{admin.name}</p>
                          <p className="text-[10px] text-[#64748B]">{admin.id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-3 text-[#475569]">{admin.email}</td>
                    <td className="py-3 px-3">
                      <RoleBadge role={admin.role} />
                    </td>
                    <td className="py-3 px-3 text-[#64748B]">{admin.department}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          admin.status === 'Active'
                            ? 'bg-[#DCFCE7] text-[#166534]'
                            : 'bg-[#FEE2E2] text-[#991B1B]'
                        }`}
                      >
                        {admin.status === 'Active' ? 'Active' : 'Suspended'}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#64748B] whitespace-nowrap">{admin.lastLogin}</td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => {
                            setEditingAdmin(admin);
                            setFormData({
                              name: admin.name,
                              email: admin.email,
                              role: admin.role,
                              department: admin.department,
                              status: admin.status,
                            });
                            setIsAddModalOpen(true);
                          }}
                          className="p-1.5 rounded-lg bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#64748B] hover:text-[#0F172A] transition-colors"
                          title="Edit Admin Account"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleToggleStatus(admin.id)}
                          className={`p-1.5 rounded-lg font-bold transition-colors text-[10px] ${
                            admin.status === 'Active'
                              ? 'bg-[#FEF2F2] text-[#EF4444] hover:bg-[#FEE2E2]'
                              : 'bg-[#DCFCE7] text-[#166534] hover:bg-[#BBF7D0]'
                          }`}
                          title={admin.status === 'Active' ? 'Suspend' : 'Activate'}
                        >
                          {admin.status === 'Active' ? 'Suspend' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ── ADD / EDIT ADMIN MODAL ────────────────────────────────── */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title={editingAdmin ? 'Edit Admin User' : 'Add New Admin User'}
        subtitle="Manage access level and department assignment"
        size="md"
      >
        <form onSubmit={handleSaveAdmin} className="space-y-4 text-xs">
          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Full Name <span className="text-[#EF4444]">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Ramesh Kulkarni"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB]"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Email Address <span className="text-[#EF4444]">*</span>
            </label>
            <input
              type="email"
              required
              placeholder="ramesh.admin@kaamsetu.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB]"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Assigned Role
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value })}
              className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB] bg-white"
            >
              {ADMIN_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Department
            </label>
            <select
              value={formData.department}
              onChange={(e) => setFormData({ ...formData, department: e.target.value })}
              className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB] bg-white"
            >
              {ADMIN_DEPARTMENTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#0F172A] mb-1">
              Account Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              className="w-full px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB] bg-white"
            >
              <option value="Active">Active</option>
              <option value="Suspended">Suspended</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#F1F5F9]">
            <button
              type="button"
              onClick={() => setIsAddModalOpen(false)}
              className="px-4 py-2 bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#475569] font-bold rounded-xl text-xs transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold rounded-xl text-xs transition-colors"
            >
              {editingAdmin ? 'Save Changes' : 'Create Admin Account'}
            </button>
          </div>
        </form>
      </Modal>
    </PageContainer>
  );
}
