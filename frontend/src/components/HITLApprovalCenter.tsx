import React, { useState } from 'react';
import { ShieldCheck, ShieldX, AlertTriangle, CheckCircle2, X } from 'lucide-react';
import { HITLTicket, UserPersona } from '../types';

interface HITLApprovalCenterProps {
  isOpen: boolean;
  onClose: () => void;
  tickets: HITLTicket[];
  currentUser: UserPersona;
  onResolveTicket: (ticketId: string, decision: 'APPROVED' | 'REJECTED', remarks: string) => Promise<void>;
}

export const HITLApprovalCenter: React.FC<HITLApprovalCenterProps> = ({
  isOpen,
  onClose,
  tickets,
  currentUser,
  onResolveTicket
}) => {
  const [selectedTicket, setSelectedTicket] = useState<HITLTicket | null>(tickets[0] || null);
  const [remarks, setRemarks] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!selectedTicket) return;
    setIsSubmitting(true);
    try {
      await onResolveTicket(selectedTicket.ticket_id, decision, remarks || `Decision recorded by ${currentUser.name}`);
      setRemarks('');
      const remaining = tickets.filter(t => t.ticket_id !== selectedTicket.ticket_id && t.status === 'PENDING');
      setSelectedTicket(remaining[0] || null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const pendingTickets = tickets.filter(t => t.status === 'PENDING');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50/70">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-amber-50 border border-amber-200 text-amber-600">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                Human-in-the-Loop (HITL) Governance & Approval Center
                <span className="text-xs bg-amber-100 text-amber-900 font-mono px-2.5 py-0.5 rounded-full font-bold border border-amber-200">
                  {pendingTickets.length} Pending
                </span>
              </h2>
              <p className="text-xs text-slate-500">
                Four-Eyes Principle enforcement for high-value financial actions, external egress, and sensitive PII unmasking.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Split Queue & Inspector */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-12 min-h-0 overflow-hidden">
          {/* Left Ticket List (5 cols) */}
          <div className="md:col-span-5 border-r border-slate-200 overflow-y-auto p-4 space-y-3 bg-slate-50">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 px-1">
              Active Intervention Queue
            </h3>
            {tickets.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-sm">
                No active intervention tickets in queue.
              </div>
            ) : (
              tickets.map((t) => {
                const isSelected = selectedTicket?.ticket_id === t.ticket_id;
                return (
                  <div
                    key={t.ticket_id}
                    onClick={() => setSelectedTicket(t)}
                    className={`p-3.5 rounded-xl border transition cursor-pointer text-left ${
                      isSelected
                        ? 'bg-white border-indigo-500 ring-2 ring-indigo-500/10 shadow-sm'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="font-mono font-bold text-indigo-700">{t.ticket_id}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        t.status === 'PENDING'
                          ? 'bg-amber-100 text-amber-800 border border-amber-200'
                          : t.status === 'APPROVED'
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                          : 'bg-rose-100 text-rose-800 border border-rose-200'
                      }`}>
                        {t.status}
                      </span>
                    </div>
                    <div className="text-xs font-bold text-slate-900 line-clamp-1">
                      {t.proposed_action}
                    </div>
                    <div className="flex items-center justify-between text-xs text-slate-500 mt-2">
                      <span>{t.requester_name}</span>
                      {t.amount_sgd > 0 && (
                        <span className="font-mono text-slate-900 font-bold">
                          S$ {t.amount_sgd.toLocaleString()}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Right Ticket Inspector & Authorization Controls (7 cols) */}
          <div className="md:col-span-7 flex flex-col justify-between overflow-y-auto p-6 bg-white">
            {selectedTicket ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-[11px] font-mono text-indigo-700 font-bold uppercase tracking-wider">
                      {selectedTicket.trigger_type.replace(/_/g, ' ')}
                    </span>
                    <h3 className="text-sm font-bold text-slate-900 mt-0.5">
                      {selectedTicket.proposed_action}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-[11px] text-slate-500 font-medium">Risk Score</span>
                    <div className="text-base font-bold text-amber-600 font-mono">
                      {(selectedTicket.risk_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>

                {/* Requester Context Pill */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500">Requester:</span>{' '}
                    <span className="text-slate-900 font-semibold">{selectedTicket.requester_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Role:</span>{' '}
                    <span className="text-indigo-700 font-mono font-medium">{selectedTicket.requester_role}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Jurisdiction:</span>{' '}
                    <span className="text-slate-900 font-semibold">{selectedTicket.requester_jurisdiction}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">Created:</span>{' '}
                    <span className="text-slate-600 font-mono">{selectedTicket.formatted_time || 'Just now'}</span>
                  </div>
                </div>

                {/* Risk Rationale */}
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5">
                  <div className="text-xs font-bold text-amber-900 flex items-center gap-1.5 mb-1">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Governance Constraint Trigger</span>
                  </div>
                  <p className="text-xs text-amber-800 leading-relaxed">
                    {selectedTicket.risk_summary}
                  </p>
                </div>

                {/* Proposed Payload Details */}
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Proposed Operation Parameters
                  </h4>
                  <pre className="bg-slate-900 text-emerald-400 rounded-xl p-3 text-[11px] font-mono overflow-x-auto max-h-36">
                    {JSON.stringify(selectedTicket.payload, null, 2)}
                  </pre>
                </div>

                {/* Existing Review Info if already resolved */}
                {selectedTicket.status !== 'PENDING' && (
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs">
                    <div className="text-slate-600">
                      Resolved by: <span className="text-slate-900 font-semibold">{selectedTicket.reviewed_by}</span>
                    </div>
                    <div className="text-slate-600 mt-1">
                      Remarks: <span className="text-slate-800 italic">"{selectedTicket.review_remarks}"</span>
                    </div>
                  </div>
                )}

                {/* Action Controls for Pending Tickets */}
                {selectedTicket.status === 'PENDING' && (
                  <div className="pt-2 border-t border-slate-200 space-y-3">
                    {!currentUser.can_approve_hitl ? (
                      <div className="bg-rose-50 border border-rose-200 rounded-xl p-3 text-xs text-rose-800">
                        ⚠️ Your active persona (<strong>{currentUser.name}</strong>) does not have Four-Eyes approval authority. Please switch to <strong>Compliance Officer</strong> or <strong>Risk Officer</strong> in the header to authorize.
                      </div>
                    ) : (
                      <>
                        <div>
                          <label className="text-xs font-bold text-slate-800 mb-1 block">
                            Four-Eyes Verification Remarks / Audit Reason:
                          </label>
                          <input
                            type="text"
                            placeholder="e.g., Verified invoice against SAP vendor registry and credit line."
                            value={remarks}
                            onChange={(e) => setRemarks(e.target.value)}
                            className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                          />
                        </div>

                        <div className="flex items-center space-x-3 pt-1">
                          <button
                            disabled={isSubmitting}
                            onClick={() => handleDecision('APPROVED')}
                            className="flex-1 flex items-center justify-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition shadow-sm disabled:opacity-50"
                          >
                            <ShieldCheck className="w-4 h-4" />
                            <span>Approve & Authorize Action</span>
                          </button>
                          <button
                            disabled={isSubmitting}
                            onClick={() => handleDecision('REJECTED')}
                            className="flex-1 flex items-center justify-center space-x-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-semibold py-2.5 px-4 rounded-xl text-xs transition disabled:opacity-50"
                          >
                            <ShieldX className="w-4 h-4" />
                            <span>Reject & Halt Execution</span>
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                Select a ticket from the queue to inspect.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
