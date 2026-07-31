import React from 'react';
import { useLocation } from 'react-router-dom';
import { Construction } from 'lucide-react';
import PageContainer from '../../components/layout/PageContainer';

export default function PlaceholderPage() {
  const location = useLocation();
  const pathName = location.pathname.split('/').pop() || 'Module';
  const formattedTitle = pathName
    .replace(/-/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());

  return (
    <PageContainer
      title={formattedTitle}
      subtitle={`KaamSetu Admin — ${formattedTitle} Management Module`}
    >
      <div className="bg-white rounded-2xl border border-[#E2E8F0] p-12 text-center space-y-4 max-w-2xl mx-auto shadow-xs my-8">
        <div className="w-16 h-16 bg-[#EFF6FF] text-[#2563EB] rounded-2xl flex items-center justify-center mx-auto shadow-xs">
          <Construction className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-[#0F172A]">
          {formattedTitle} Module Shell
        </h3>
        <p className="text-xs text-[#64748B] leading-relaxed">
          The layout and routing for <span className="font-bold text-[#0F172A]">{formattedTitle}</span> is configured.
          The complete management interface for this module will be connected in subsequent steps.
        </p>
      </div>
    </PageContainer>
  );
}
