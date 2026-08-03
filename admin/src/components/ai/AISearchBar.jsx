import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Sparkles, Search, X, TrendingUp, Clock, Loader2 } from 'lucide-react';
import { aiSearch } from '../../services/aiService';
import { useNavigate } from 'react-router-dom';

export default function AISearchBar({ placeholder = 'AI Search — services, workers, categories...' }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [trending, setTrending] = useState([]);
  const [results, setResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingSugg, setIsLoadingSugg] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const debounceRef = useRef(null);
  const inputRef = useRef(null);
  const panelRef = useRef(null);

  // Load trending on mount
  useEffect(() => {
    aiSearch.trending()
      .then((data) => setTrending(Array.isArray(data) ? data.slice(0, 5) : []))
      .catch(() => {});
  }, []);

  // Click outside to close
  useEffect(() => {
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setIsFocused(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const fetchSuggestions = useCallback(async (q) => {
    if (q.length < 2) { setSuggestions([]); return; }
    setIsLoadingSugg(true);
    try {
      const data = await aiSearch.suggestions(q);
      setSuggestions(Array.isArray(data) ? data.slice(0, 6) : []);
    } catch { setSuggestions([]); }
    finally { setIsLoadingSugg(false); }
  }, []);

  const handleInputChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    setResults(null);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => fetchSuggestions(val), 300);
  };

  const handleSearch = async (q = query) => {
    const trimmed = q.trim();
    if (!trimmed) return;
    setQuery(trimmed);
    setIsSearching(true);
    setSuggestions([]);
    try {
      const data = await aiSearch.query({ query: trimmed, page: 1, page_size: 8 });
      setResults(data);
    } catch { setResults({ results: [], total: 0 }); }
    finally { setIsSearching(false); }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSearch();
    if (e.key === 'Escape') { setIsFocused(false); inputRef.current?.blur(); }
  };

  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setResults(null);
    inputRef.current?.focus();
  };

  const showDropdown = isFocused && (suggestions.length > 0 || trending.length > 0 || results);

  const getTypeIcon = (type) => {
    if (type === 'trending') return <TrendingUp className="w-3 h-3 text-[#F59E0B]" />;
    if (type === 'recent') return <Clock className="w-3 h-3 text-[#94A3B8]" />;
    return <Sparkles className="w-3 h-3 text-[#7C3AED]" />;
  };

  return (
    <div className="relative w-full" ref={panelRef}>
      {/* Input */}
      <div className={`flex items-center gap-2 bg-[#F8FAFC] border rounded-xl px-3 py-2 transition-all ${
        isFocused ? 'border-[#7C3AED] ring-2 ring-[#7C3AED]/15 bg-white shadow-sm' : 'border-[#E2E8F0]'
      }`}>
        {isSearching
          ? <Loader2 className="w-4 h-4 text-[#7C3AED] animate-spin shrink-0" />
          : <Sparkles className={`w-4 h-4 shrink-0 transition-colors ${isFocused ? 'text-[#7C3AED]' : 'text-[#94A3B8]'}`} />
        }
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={() => setIsFocused(true)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="flex-1 text-xs text-[#0F172A] placeholder-[#94A3B8] bg-transparent outline-none font-medium"
        />
        {query && (
          <button onClick={handleClear} className="text-[#94A3B8] hover:text-[#475569] transition-colors">
            <X className="w-3.5 h-3.5" />
          </button>
        )}
        <button
          onClick={() => handleSearch()}
          className="px-2.5 py-1 rounded-lg bg-[#7C3AED] text-white text-[10px] font-bold hover:bg-[#6D28D9] transition-colors"
        >
          Search
        </button>
      </div>

      {/* Dropdown Panel */}
      {showDropdown && (
        <div className="absolute top-full mt-1.5 w-full bg-white rounded-2xl border border-[#E2E8F0] shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
          {/* AI Badge */}
          <div className="flex items-center gap-1.5 px-3 py-2 border-b border-[#F1F5F9] bg-gradient-to-r from-[#F5F3FF] to-[#EFF6FF]">
            <Sparkles className="w-3 h-3 text-[#7C3AED]" />
            <span className="text-[10px] font-bold text-[#7C3AED]">AI-Powered Intelligent Search</span>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="py-1">
              <p className="px-3 py-1 text-[9px] font-bold text-[#94A3B8] uppercase tracking-wider">Suggestions</p>
              {isLoadingSugg && (
                <div className="px-3 py-2 flex items-center gap-2">
                  <Loader2 className="w-3 h-3 text-[#7C3AED] animate-spin" />
                  <span className="text-[11px] text-[#94A3B8]">Loading...</span>
                </div>
              )}
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSearch(s.suggestion || s)}
                  className="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-[#F8FAFC] transition-colors text-left"
                >
                  {getTypeIcon(s.type)}
                  <span className="text-[11px] text-[#0F172A] font-medium">{s.suggestion || s}</span>
                  {s.type && (
                    <span className="ml-auto text-[9px] text-[#94A3B8] capitalize">{s.type}</span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Trending (when no query) */}
          {!query && trending.length > 0 && (
            <div className="py-1 border-t border-[#F1F5F9]">
              <p className="px-3 py-1 text-[9px] font-bold text-[#94A3B8] uppercase tracking-wider">Trending Searches</p>
              <div className="flex flex-wrap gap-1.5 px-3 pb-2">
                {trending.map((t, i) => (
                  <button
                    key={i}
                    onClick={() => handleSearch(t)}
                    className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-[#FEF3C7] text-[#92400E] text-[10px] font-semibold hover:bg-[#FDE68A] transition-colors"
                  >
                    <TrendingUp className="w-2.5 h-2.5" />
                    {t}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {results && (
            <div className="border-t border-[#F1F5F9]">
              <div className="flex items-center justify-between px-3 py-1.5">
                <p className="text-[9px] font-bold text-[#94A3B8] uppercase tracking-wider">Results</p>
                <p className="text-[9px] text-[#94A3B8]">{results.total} found</p>
              </div>
              {results.results?.length === 0 && (
                <p className="px-3 py-3 text-[11px] text-[#94A3B8] text-center">No results found for "{query}"</p>
              )}
              {results.results?.slice(0, 5).map((item, i) => (
                <div key={i} className="flex items-start gap-2.5 px-3 py-2 hover:bg-[#F8FAFC] transition-colors border-t border-[#F1F5F9]/50 cursor-pointer">
                  <div className={`p-1.5 rounded-lg shrink-0 ${item.item_type === 'worker' ? 'bg-[#D1FAE5]' : 'bg-[#EFF6FF]'}`}>
                    <Search className={`w-3 h-3 ${item.item_type === 'worker' ? 'text-[#059669]' : 'text-[#2563EB]'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <p className="text-[11px] font-bold text-[#0F172A] truncate">{item.title}</p>
                      <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded-full capitalize shrink-0 ${
                        item.item_type === 'worker' ? 'bg-[#D1FAE5] text-[#059669]' : 'bg-[#EFF6FF] text-[#2563EB]'
                      }`}>{item.item_type}</span>
                    </div>
                    {item.reasons?.[0] && (
                      <p className="text-[9px] text-[#64748B] mt-0.5 truncate">{item.reasons[0]}</p>
                    )}
                  </div>
                  <span className="text-[9px] font-bold text-[#7C3AED] shrink-0">
                    {Math.round(item.relevance_score * 100)}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
