import React, { useState, useRef, useEffect, useCallback } from 'react';
import { X, Send, Bot, Sparkles, RotateCw, ChevronDown, Shield, HardHat, Users } from 'lucide-react';
import { aiAssistant } from '../../services/aiService';
import aiAvatarUrl from '../../assets/ai_avatar.png';

const ROLES = [
  { id: 'admin', label: 'Admin', icon: Shield, color: 'text-[#7C3AED]', bg: 'bg-[#F5F3FF]' },
  { id: 'customer', label: 'Customer', icon: Users, color: 'text-[#2563EB]', bg: 'bg-[#EFF6FF]' },
  { id: 'worker', label: 'Worker', icon: HardHat, color: 'text-[#059669]', bg: 'bg-[#D1FAE5]' },
];

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-3 py-2">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-[#94A3B8] animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
}

export default function AIAssistantWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [role, setRole] = useState('admin');
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showRoleMenu, setShowRoleMenu] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
      if (messages.length === 0) {
        setMessages([{
          id: 'welcome',
          role: 'assistant',
          content: `Hi! I'm **KaamSetu AI Assistant** operating in **${role.charAt(0).toUpperCase() + role.slice(1)}** mode. I have access to live platform data — ask me about bookings, workers, analytics, or platform metrics.`,
          grounded: false,
          tools_called: [],
        }]);
      }
    }
  }, [isOpen]);

  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setSessionId(null);
    setMessages([{
      id: 'role-change',
      role: 'assistant',
      content: `Switched to **${newRole.charAt(0).toUpperCase() + newRole.slice(1)}** mode. Session reset. How can I help?`,
      grounded: false,
      tools_called: [],
    }]);
    setShowRoleMenu(false);
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMsg = { id: Date.now(), role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await aiAssistant.chat({
        message: text,
        session_id: sessionId || undefined,
        role,
        admin_id: role === 'admin' ? 'admin' : undefined,
        user_id: role === 'customer' ? 'demo_user' : undefined,
        worker_id: role === 'worker' ? 'demo_worker' : undefined,
      });

      if (!sessionId) setSessionId(res.session_id);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: res.response,
          grounded: res.grounded,
          tools_called: res.tools_called || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content: `Sorry, I couldn't reach the AI service right now. Please ensure the AI microservice is running on \`${import.meta.env.VITE_AI_SERVICE_URL || 'http://localhost:8000'}\`.`,
          grounded: false,
          tools_called: [],
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setMessages([{
      id: 'reset',
      role: 'assistant',
      content: 'Session cleared. Ready to help!',
      grounded: false,
      tools_called: [],
    }]);
  };

  const activeRole = ROLES.find((r) => r.id === role);
  const RoleIcon = activeRole.icon;

  const renderMessage = (msg) => {
    // Very simple markdown: **bold**
    return msg.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  };

  return (
    <>
      {/* Floating Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 z-40 group transition-all duration-300 ${isOpen ? 'scale-0 opacity-0 pointer-events-none' : 'scale-100 opacity-100'}`}
        aria-label="Open AI Assistant"
      >
        <div className="relative">
          {/* Pulse ring */}
          <span className="absolute inset-0 rounded-full bg-[#7C3AED]/20 animate-ping" />
          <div className="relative w-14 h-14 rounded-full shadow-xl shadow-[#7C3AED]/30 overflow-hidden ring-4 ring-white hover:ring-[#7C3AED]/30 transition-all duration-200 hover:scale-110">
            <img src={aiAvatarUrl} alt="AI Assistant" className="w-full h-full object-cover" />
          </div>
          {/* Online dot */}
          <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-[#10B981] rounded-full ring-2 ring-white flex items-center justify-center">
            <span className="w-2 h-2 bg-[#10B981] rounded-full animate-pulse" />
          </span>
        </div>
      </button>

      {/* Chat Panel */}
      <div
        className={`fixed bottom-6 right-6 z-50 w-[380px] max-h-[600px] flex flex-col bg-white rounded-3xl shadow-2xl shadow-[#0F172A]/20 ring-1 ring-[#E2E8F0] transition-all duration-300 origin-bottom-right ${
          isOpen ? 'scale-100 opacity-100' : 'scale-75 opacity-0 pointer-events-none'
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#F1F5F9] bg-gradient-to-r from-[#7C3AED] to-[#2563EB] rounded-t-3xl">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl overflow-hidden ring-2 ring-white/30">
              <img src={aiAvatarUrl} alt="AI" className="w-full h-full object-cover" />
            </div>
            <div>
              <p className="text-xs font-black text-white">KaamSetu AI</p>
              <p className="text-[10px] text-white/70 font-medium">RAG-Grounded Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Role selector */}
            <div className="relative">
              <button
                onClick={() => setShowRoleMenu(!showRoleMenu)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-xl text-[10px] font-bold bg-white/20 text-white hover:bg-white/30 transition-colors`}
              >
                <RoleIcon className="w-3 h-3" />
                {activeRole.label}
                <ChevronDown className="w-3 h-3" />
              </button>
              {showRoleMenu && (
                <div className="absolute right-0 top-full mt-1 bg-white rounded-xl shadow-xl border border-[#E2E8F0] overflow-hidden z-10 min-w-[130px]">
                  {ROLES.map((r) => {
                    const RIcon = r.icon;
                    return (
                      <button
                        key={r.id}
                        onClick={() => handleRoleChange(r.id)}
                        className={`w-full flex items-center gap-2 px-3 py-2 text-[11px] font-semibold hover:bg-[#F8FAFC] transition-colors ${r.color} ${role === r.id ? r.bg : ''}`}
                      >
                        <RIcon className="w-3.5 h-3.5" />
                        {r.label}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <button onClick={handleReset} className="p-1.5 rounded-xl text-white/70 hover:text-white hover:bg-white/20 transition-colors" title="Reset session">
              <RotateCw className="w-3.5 h-3.5" />
            </button>
            <button onClick={() => setIsOpen(false)} className="p-1.5 rounded-xl text-white/70 hover:text-white hover:bg-white/20 transition-colors">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 max-h-[400px]">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {msg.role === 'assistant' && (
                <div className="w-7 h-7 rounded-xl overflow-hidden shrink-0 mt-0.5">
                  <img src={aiAvatarUrl} alt="AI" className="w-full h-full object-cover" />
                </div>
              )}
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                <div
                  className={`px-3.5 py-2.5 rounded-2xl text-[12px] leading-relaxed font-medium ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-[#7C3AED] to-[#2563EB] text-white rounded-tr-sm'
                      : msg.isError
                      ? 'bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA] rounded-tl-sm'
                      : 'bg-[#F8FAFC] text-[#0F172A] border border-[#E2E8F0] rounded-tl-sm'
                  }`}
                  dangerouslySetInnerHTML={{ __html: renderMessage(msg) }}
                />
                {msg.role === 'assistant' && !msg.isError && (
                  <div className="flex items-center gap-2 flex-wrap">
                    {msg.grounded && (
                      <span className="flex items-center gap-1 text-[9px] font-bold text-[#059669] bg-[#D1FAE5] px-2 py-0.5 rounded-full">
                        <Sparkles className="w-2.5 h-2.5" />
                        Verified Platform Data
                      </span>
                    )}
                    {msg.tools_called?.length > 0 && (
                      <span className="text-[9px] text-[#94A3B8] font-medium">
                        Tool: {msg.tools_called[0]}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-2 justify-start">
              <div className="w-7 h-7 rounded-xl overflow-hidden shrink-0">
                <img src={aiAvatarUrl} alt="AI" className="w-full h-full object-cover" />
              </div>
              <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-2xl rounded-tl-sm">
                <TypingIndicator />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-3 border-t border-[#F1F5F9]">
          <div className="flex items-center gap-2 bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] focus-within:border-[#7C3AED] focus-within:ring-2 focus-within:ring-[#7C3AED]/10 transition-all px-3 py-2">
            <Bot className="w-4 h-4 text-[#94A3B8] shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Ask about bookings, analytics..."
              className="flex-1 text-xs text-[#0F172A] placeholder-[#94A3B8] bg-transparent outline-none font-medium"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="p-1.5 rounded-xl bg-gradient-to-br from-[#7C3AED] to-[#2563EB] text-white disabled:opacity-40 hover:scale-110 transition-all disabled:hover:scale-100"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
          <p className="text-[9px] text-[#94A3B8] text-center mt-1.5 font-medium">
            Grounded in live KaamSetu platform data
          </p>
        </div>
      </div>

      {/* Backdrop for role menu */}
      {showRoleMenu && (
        <div className="fixed inset-0 z-40" onClick={() => setShowRoleMenu(false)} />
      )}
    </>
  );
}
