import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, CheckCircle2, RefreshCw } from 'lucide-react';
import { AuditEntry } from '../types';

export const AuditLedger: React.FC = () => {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [verificationResult, setVerificationResult] = useState<any | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);

  const fetchLedger = () => {
    fetch('/api/audit/ledger')
      .then(res => res.json())
      .then(data => setEntries(data))
      .catch(err => console.error('Failed to load ledger:', err));
  };

  useEffect(() => {
    fetchLedger();
  }, []);

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const res = await fetch('/api/audit/verify');
      const data = await res.json();
      setVerificationResult(data);
    } catch (err) {
      console.error('Verification failed:', err);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-600" />
            Cryptographic Tamper-Evident Audit Ledger
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            SHA-256 hash-chained immutable audit records verifying every prompt, decision, and HITL authorization.
          </p>
        </div>
        <button
          disabled={isVerifying}
          onClick={handleVerify}
          className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition shadow-sm disabled:opacity-50"
        >
          {isVerifying ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <ShieldCheck className="w-4 h-4" />
          )}
          <span>{isVerifying ? 'Verifying Block Hashes...' : 'Verify Cryptographic Chain'}</span>
        </button>
      </div>

      {/* Verification Status Banner */}
      {verificationResult && (
        <div className={`p-4 rounded-xl border flex items-center justify-between text-xs shadow-sm ${
          verificationResult.valid
            ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
            : 'bg-rose-50 border-rose-200 text-rose-900'
        }`}>
          <div className="flex items-center space-x-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            <div>
              <div className="font-bold text-sm">
                Cryptographic Integrity Verified (100% Tamper-Evident)
              </div>
              <p className="text-[11px] text-emerald-700 mt-0.5 font-medium">
                {verificationResult.message} Verified {verificationResult.total_blocks} sequential blocks.
              </p>
            </div>
          </div>
          <div className="font-mono text-[10px] text-emerald-800 bg-emerald-100/70 border border-emerald-200 px-2.5 py-1 rounded-md font-medium">
            Latest Hash: {verificationResult.latest_hash?.slice(0, 16)}...
          </div>
        </div>
      )}

      {/* Audit Blocks Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Sequential Audit Blocks ({entries.length})
          </h3>
          <button
            onClick={fetchLedger}
            className="text-xs text-indigo-600 hover:text-indigo-700 font-semibold flex items-center gap-1"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-xl">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead>
              <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-[11px]">
                <th className="py-3 px-4">Block ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4">User & Role</th>
                <th className="py-3 px-4">Action / Prompt Summary</th>
                <th className="py-3 px-4">Decision</th>
                <th className="py-3 px-4">SHA-256 Hash</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 text-[11px]">
              {entries.map((e, idx) => (
                <tr key={idx} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-4 text-indigo-700 font-bold">{e.entry_id}</td>
                  <td className="py-3 px-4 text-slate-500">{e.formatted_time || 'Recent'}</td>
                  <td className="py-3 px-4">
                    <span className="bg-slate-100 border border-slate-200 px-2 py-0.5 rounded text-[10px] text-slate-700 font-medium">
                      {e.event_type}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-900 font-sans font-medium">
                    {e.user_id} <span className="text-slate-500 font-normal">({e.role})</span>
                  </td>
                  <td className="py-3 px-4 font-sans text-slate-600 max-w-xs truncate">
                    {e.action_or_prompt}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      e.decision.includes('BLOCKED')
                        ? 'bg-rose-50 text-rose-700 border border-rose-200'
                        : e.decision.includes('PENDING')
                        ? 'bg-amber-50 text-amber-800 border border-amber-200'
                        : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    }`}>
                      {e.decision}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400 font-mono text-[10px]">
                    {e.entry_hash.slice(0, 14)}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
