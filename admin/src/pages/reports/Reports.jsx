import React, { useState } from 'react';
import {
  FileChartColumn,
  Download,
  Eye,
  FileText,
  FileSpreadsheet,
  FileCode,
  Filter,
  Plus,
  Search,
  Calendar,
  CheckCircle2,
  Clock,
  Trash2,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

import PageContainer from '../../components/layout/PageContainer';
import Modal from '../../components/common/Modal';
import EmptyState from '../../components/common/EmptyState';
import { useToast } from '../../components/common/ToastContext';
import {
  REPORT_CATEGORIES,
  AVAILABLE_REPORTS,
  RECENT_REPORTS_HISTORY,
} from '../../data/reports';

export default function Reports() {
  const { addToast } = useToast();
  const [selectedCategory, setSelectedCategory] = useState('All Reports');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCity, setSelectedCity] = useState('All Cities');
  const [selectedFormat, setSelectedFormat] = useState('All Formats');
  const [history, setHistory] = useState(RECENT_REPORTS_HISTORY);
  const [previewReport, setPreviewReport] = useState(null);
  const [generatingReportId, setGeneratingReportId] = useState(null);

  // Filter available reports
  const filteredReports = AVAILABLE_REPORTS.filter((rep) => {
    const matchesCategory =
      selectedCategory === 'All Reports' || rep.category === selectedCategory;
    const matchesSearch =
      rep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      rep.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleGenerate = (report) => {
    setGeneratingReportId(report.id);
    setTimeout(() => {
      setGeneratingReportId(null);
      const newEntry = {
        id: `HIST-${Math.floor(1000 + Math.random() * 9000)}`,
        reportName: report.title,
        category: report.category,
        generatedBy: 'Super Admin (Current Session)',
        generatedOn: new Date().toLocaleString('en-IN', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        }),
        format: report.supportedFormats[0] || 'PDF',
        size: '1.8 MB',
        status: 'Completed',
      };
      setHistory([newEntry, ...history]);
      addToast({
        title: 'Report Compiled',
        message: `Successfully generated "${report.title}"`,
        type: 'success',
      });
    }, 800);
  };

  const handleDownload = (historyItem) => {
    addToast({
      title: 'Download Initiated',
      message: `Downloading ${historyItem.reportName} (${historyItem.format})`,
      type: 'info',
    });
  };

  const handleDeleteHistory = (id) => {
    setHistory(history.filter((item) => item.id !== id));
    addToast({
      title: 'Record Removed',
      message: 'Report history entry deleted.',
      type: 'warning',
    });
  };

  const getFormatBadge = (fmt) => {
    switch (fmt) {
      case 'PDF':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold bg-[#FEE2E2] text-[#991B1B] border border-[#FECACA]">
            <FileText className="w-3 h-3 text-[#DC2626]" /> PDF
          </span>
        );
      case 'Excel':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold bg-[#DCFCE7] text-[#166534] border border-[#BBF7D0]">
            <FileSpreadsheet className="w-3 h-3 text-[#16A34A]" /> Excel
          </span>
        );
      case 'CSV':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold bg-[#E0F2FE] text-[#075985] border border-[#BAE6FD]">
            <FileCode className="w-3 h-3 text-[#0EA5E9]" /> CSV
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <PageContainer
      title="Reports Center"
      subtitle="Central hub for generating and exporting platform business reports."
    >
      <div className="space-y-6">
        {/* ── CATEGORY TABS & FILTERS ──────────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-4 shadow-xs space-y-4">
          {/* Category Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
            {REPORT_CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-[#2563EB] text-white shadow-xs'
                    : 'bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#64748B] hover:text-[#0F172A] border border-[#E2E8F0]'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Filter Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2 border-t border-[#F1F5F9]">
            {/* Search */}
            <div className="relative">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search report titles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-xl border border-[#E2E8F0] text-xs focus:outline-none focus:border-[#2563EB]"
              />
            </div>

            {/* City Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs">
              <span className="text-[#64748B] font-medium">City:</span>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="bg-transparent focus:outline-none cursor-pointer text-[#0F172A] font-bold w-full"
              >
                <option value="All Cities">All Cities</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Pune">Pune</option>
                <option value="Navi Mumbai">Navi Mumbai</option>
                <option value="Thane">Thane</option>
                <option value="Nagpur">Nagpur</option>
              </select>
            </div>

            {/* Format Filter */}
            <div className="flex items-center gap-2 bg-[#F8FAFC] px-3 py-2 rounded-xl border border-[#E2E8F0] text-xs">
              <span className="text-[#64748B] font-medium">Format:</span>
              <select
                value={selectedFormat}
                onChange={(e) => setSelectedFormat(e.target.value)}
                className="bg-transparent focus:outline-none cursor-pointer text-[#0F172A] font-bold w-full"
              >
                <option value="All Formats">All Formats (PDF/Excel/CSV)</option>
                <option value="PDF">PDF</option>
                <option value="Excel">Excel</option>
                <option value="CSV">CSV</option>
              </select>
            </div>

            {/* Reset Filters */}
            <button
              onClick={() => {
                setSelectedCategory('All Reports');
                setSearchQuery('');
                setSelectedCity('All Cities');
                setSelectedFormat('All Formats');
              }}
              className="py-2 px-3 rounded-xl border border-[#E2E8F0] bg-white hover:bg-[#F8FAFC] text-xs font-bold text-[#64748B] hover:text-[#0F172A] transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Reset Filters
            </button>
          </div>
        </div>

        {/* ── REPORT CARDS GRID ───────────────────────────────────── */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-extrabold text-[#0F172A] uppercase tracking-wide">
              Available Reports ({filteredReports.length})
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="bg-white rounded-2xl border border-[#E2E8F0] p-5 shadow-xs hover:shadow-md hover:border-[#CBD5E1] transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE]">
                      {report.category}
                    </span>
                    <span className="text-[11px] font-semibold text-[#94A3B8]">
                      {report.frequency}
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-[#0F172A] leading-snug">
                    {report.title}
                  </h4>

                  <p className="text-xs text-[#64748B] line-clamp-2 leading-relaxed">
                    {report.description}
                  </p>
                </div>

                <div className="space-y-3 pt-3 border-t border-[#F1F5F9]">
                  <div className="flex items-center justify-between text-[11px] text-[#94A3B8]">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" /> Last: {report.lastGenerated}
                    </span>
                    <div className="flex items-center gap-1">
                      {report.supportedFormats.map((fmt) => (
                        <span key={fmt} className="font-bold text-[#475569]">
                          {fmt}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleGenerate(report)}
                      disabled={generatingReportId === report.id}
                      className="flex-1 py-2 px-3 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold rounded-xl transition-colors shadow-xs flex items-center justify-center gap-1.5 disabled:opacity-50"
                    >
                      {generatingReportId === report.id ? (
                        <>
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Generating...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3.5 h-3.5" /> Generate Report
                        </>
                      )}
                    </button>

                    <button
                      onClick={() => setPreviewReport(report)}
                      className="p-2 bg-[#F8FAFC] hover:bg-[#F1F5F9] text-[#64748B] hover:text-[#0F172A] rounded-xl border border-[#E2E8F0] transition-colors"
                      title="Preview Report Template"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── RECENT REPORTS HISTORY TABLE ─────────────────────────── */}
        <div className="bg-white rounded-2xl border border-[#E2E8F0] p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-extrabold text-[#0F172A]">
                Recent Generated Reports Log
              </h3>
              <p className="text-xs text-[#64748B]">History of reports compiled across admin sessions</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-[#F1F5F9] text-[#94A3B8] font-bold uppercase tracking-wider">
                  <th className="pb-3 px-3">Report Name</th>
                  <th className="pb-3 px-3">Generated By</th>
                  <th className="pb-3 px-3">Generated On</th>
                  <th className="pb-3 px-3">Format</th>
                  <th className="pb-3 px-3">File Size</th>
                  <th className="pb-3 px-3">Status</th>
                  <th className="pb-3 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] font-medium text-[#0F172A]">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-[#F8FAFC] transition-colors">
                    <td className="py-3 px-3 font-bold text-[#0F172A]">
                      {item.reportName}
                    </td>
                    <td className="py-3 px-3 text-[#475569]">{item.generatedBy}</td>
                    <td className="py-3 px-3 text-[#64748B]">{item.generatedOn}</td>
                    <td className="py-3 px-3">{getFormatBadge(item.format)}</td>
                    <td className="py-3 px-3 text-[#64748B] font-semibold">{item.size}</td>
                    <td className="py-3 px-3">
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold text-[#16A34A] bg-[#DCFCE7] px-2 py-0.5 rounded-md">
                        <CheckCircle2 className="w-3 h-3" /> {item.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleDownload(item)}
                          className="p-1.5 rounded-lg bg-[#EFF6FF] text-[#2563EB] hover:bg-[#DBEAFE] font-bold transition-colors"
                          title="Download"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteHistory(item.id)}
                          className="p-1.5 rounded-lg bg-[#FEF2F2] text-[#EF4444] hover:bg-[#FEE2E2] font-bold transition-colors"
                          title="Delete Log Entry"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
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

      {/* ── PREVIEW MODAL ─────────────────────────────────────────── */}
      <Modal
        isOpen={Boolean(previewReport)}
        onClose={() => setPreviewReport(null)}
        title="Report Template Preview"
        subtitle={previewReport?.title}
        footer={
          <>
            <button
              onClick={() => setPreviewReport(null)}
              className="px-4 py-2 bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#475569] font-bold rounded-xl text-xs transition-colors"
            >
              Close Preview
            </button>
            <button
              onClick={() => {
                handleGenerate(previewReport);
                setPreviewReport(null);
              }}
              className="px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-bold rounded-xl text-xs transition-colors"
            >
              Generate Now
            </button>
          </>
        }
      >
        {previewReport && (
          <div className="space-y-3 text-xs">
            <div>
              <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Report Title</p>
              <p className="text-sm font-extrabold text-[#0F172A] mt-0.5">{previewReport.title}</p>
            </div>

            <div>
              <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Category & Frequency</p>
              <p className="text-xs font-semibold text-[#475569] mt-0.5">
                {previewReport.category} • {previewReport.frequency}
              </p>
            </div>

            <div>
              <p className="text-[11px] font-bold text-[#94A3B8] uppercase">Description</p>
              <p className="text-xs text-[#64748B] mt-0.5 leading-relaxed">{previewReport.description}</p>
            </div>

            <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] space-y-2">
              <p className="text-xs font-bold text-[#0F172A]">Sample Output Columns Preview:</p>
              <ul className="list-disc list-inside text-xs text-[#475569] space-y-1 font-medium">
                <li>Transaction ID / Job Reference</li>
                <li>Customer & Worker KYC Identifiers</li>
                <li>Gross Amount, Platform Fee % & Net Payout</li>
                <li>City, Service Category & Timestamp</li>
              </ul>
            </div>
          </div>
        )}
      </Modal>
    </PageContainer>
  );
}
