import React, { useState, useEffect } from 'react';
import {
  Database,
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Lock,
  Key,
  UserCheck
} from 'lucide-react';
import { GoldAnalytics, UserPersona } from '../types';

interface MedallionLineageProps {
  currentUser?: UserPersona;
  selectedPersonaKey?: string;
}

export const MedallionLineage: React.FC<MedallionLineageProps> = ({
  currentUser,
  selectedPersonaKey
}) => {
  const [analytics, setAnalytics] = useState<GoldAnalytics | null>(null);
  const [activeTier, setActiveTier] = useState<'BRONZE' | 'SILVER' | 'QUARANTINE'>('SILVER');
  const [tierData, setTierData] = useState<any[]>([]);
  const [runningPipeline, setRunningPipeline] = useState(false);
  const [pipelineMessage, setPipelineMessage] = useState<string | null>(null);
  const [accessDeniedError, setAccessDeniedError] = useState<string | null>(null);

  const isDataEngineer = currentUser?.role === 'DATA_ENGINEER';
  const isBronzeBlocked = activeTier === 'BRONZE' && !isDataEngineer;

  const fetchAnalytics = async () => {
    try {
      const res = await fetch('/api/medallion/analytics');
      const data = await res.json();
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  };

  const fetchTierData = async (tier: string) => {
    try {
      const param = selectedPersonaKey ? `?user_persona_key=${encodeURIComponent(selectedPersonaKey)}` : '';
      const res = await fetch(`/api/medallion/tier/${tier}${param}`);
      if (!res.ok) {
        if (res.status === 403) {
          const errData = await res.json();
          setAccessDeniedError(errData.detail || 'Access Denied: PoLP tier restriction');
          setTierData([]);
          return;
        }
        throw new Error(`Failed to load tier data: HTTP ${res.status}`);
      }
      const data = await res.json();
      setAccessDeniedError(null);
      setTierData(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load tier data:', err);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    fetchTierData(activeTier);
    const interval = setInterval(() => {
      fetchAnalytics();
      fetchTierData(activeTier);
    }, 4000);
    return () => clearInterval(interval);
  }, [activeTier, selectedPersonaKey]);

  const handleRunPipeline = async () => {
    setRunningPipeline(true);
    setPipelineMessage(null);
    try {
      const res = await fetch('/api/medallion/run-pipeline', { method: 'POST' });
      const data = await res.json();
      setPipelineMessage(`Pipeline cycle completed: ${data.pipeline_summary.silver_promoted} promoted to Silver, ${data.pipeline_summary.quarantined} quarantined under contract.`);
      await fetchAnalytics();
      await fetchTierData(activeTier);
    } catch (err) {
      console.error('Pipeline error:', err);
    } finally {
      setRunningPipeline(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Trigger Button */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Database className="w-5 h-5 text-indigo-600" />
            Medallion Data Lakehouse & Dynamic Guardrails
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Automated schema validation, sensitive JAPAC PII pseudonymization, PoLP access boundaries, and certified Gold AI-ready aggregations.
          </p>
        </div>
        <button
          disabled={runningPipeline}
          onClick={handleRunPipeline}
          className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition shadow-sm disabled:opacity-50"
        >
          {runningPipeline ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span>{runningPipeline ? 'Enforcing Contracts...' : 'Run Medallion Inspection'}</span>
        </button>
      </div>

      {pipelineMessage && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs p-4 rounded-xl flex items-center gap-2.5 shadow-sm">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span className="font-medium">{pipelineMessage}</span>
        </div>
      )}

      {/* Gold Certified KPIs */}
      {analytics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Certified Transactions (Gold)</span>
            <div className="text-2xl font-bold text-slate-900 font-mono mt-1">
              {analytics.total_certified_transactions}
            </div>
            <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-mono mt-2 inline-block font-medium">
              100% PII Masked & Tokenized
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Total Volume (SGD Base)</span>
            <div className="text-2xl font-bold text-indigo-700 font-mono mt-1">
              S$ {analytics.total_volume_sgd.toLocaleString()}
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">
              FAST, PayNow & Cross-Border
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Equivalent Volume (INR Base)</span>
            <div className="text-2xl font-bold text-amber-700 font-mono mt-1">
              ₹ {analytics.total_volume_inr.toLocaleString()}
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">
              Normalized at 1 SGD = ~64.5 INR
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Compliance Health Score</span>
            <div className="text-2xl font-bold text-emerald-700 font-mono mt-1">
              {analytics.compliance_health_score}%
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">
              {analytics.quarantine_count} Quarantine Rejections Isolated
            </span>
          </div>
        </div>
      )}

      {/* Visual Medallion Flow Pipeline */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-4">
          Interactive Medallion Architecture (Click a Tier to Inspect Records)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Bronze Card */}
          <div
            onClick={() => setActiveTier('BRONZE')}
            className={`p-4 rounded-xl border transition cursor-pointer text-left ${
              activeTier === 'BRONZE'
                ? 'bg-amber-50/60 border-amber-400 ring-2 ring-amber-400/20 shadow-sm'
                : 'bg-slate-50 border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-amber-900">1. Bronze (Raw Lake)</span>
              {isDataEngineer ? (
                <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-600" /> Engineer Access
                </span>
              ) : (
                <span className="text-[10px] font-mono bg-rose-100 text-rose-800 px-2 py-0.5 rounded font-semibold flex items-center gap-1">
                  <Lock className="w-3 h-3 text-rose-600" /> PoLP Blocked
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Unprocessed financial streams containing raw Singapore NRIC, Indian PAN, dirty schemas, and unmasked accounts. Restricted by PoLP.
            </p>
          </div>

          {/* Silver Card */}
          <div
            onClick={() => setActiveTier('SILVER')}
            className={`p-4 rounded-xl border transition cursor-pointer text-left ${
              activeTier === 'SILVER'
                ? 'bg-indigo-50/60 border-indigo-500 ring-2 ring-indigo-500/20 shadow-sm'
                : 'bg-slate-50 border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-indigo-900">2. Silver (Curated)</span>
              <span className="text-[10px] font-mono bg-indigo-100 text-indigo-800 px-2 py-0.5 rounded font-semibold">
                PII-Masked
              </span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Contract-enforced tier with NRIC/PAN dynamic masking, FX normalization, and deduplication. Safe for business analysts.
            </p>
          </div>

          {/* Quarantine Card */}
          <div
            onClick={() => setActiveTier('QUARANTINE')}
            className={`p-4 rounded-xl border transition cursor-pointer text-left ${
              activeTier === 'QUARANTINE'
                ? 'bg-rose-50/60 border-rose-400 ring-2 ring-rose-400/20 shadow-sm'
                : 'bg-slate-50 border-slate-200 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-rose-900">3. Quarantine Vault</span>
              <span className="text-[10px] font-mono bg-rose-100 text-rose-800 px-2 py-0.5 rounded font-semibold">
                Contract Breaches
              </span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Corrupt payloads, negative transactions, or invalid currencies quarantined for compliance and risk audit review.
            </p>
          </div>

          {/* Gold Certified */}
          <div className="p-4 rounded-xl border bg-emerald-50/50 border-emerald-300 text-left">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-emerald-900">4. Gold (Certified AI-Ready)</span>
              <span className="text-[10px] font-mono bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-semibold">
                Certified
              </span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Verified, de-identified aggregations exposed strictly to downstream AI copilots and analyst queries.
            </p>
          </div>
        </div>
      </div>

      {/* Tier Records Table Viewer */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm overflow-hidden">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Viewing Tier:
            </h3>
            <span className={`font-mono text-xs font-bold px-2.5 py-0.5 rounded-md ${
              activeTier === 'BRONZE'
                ? 'bg-amber-100 text-amber-800 border border-amber-300'
                : activeTier === 'QUARANTINE'
                ? 'bg-rose-100 text-rose-800 border border-rose-300'
                : 'bg-indigo-50 text-indigo-700 border border-indigo-200'
            }`}>
              {activeTier}
            </span>
          </div>
          <span className="text-xs text-slate-500">
            {isBronzeBlocked ? '0 records (Access Blocked)' : `Showing ${tierData.length} records`}
          </span>
        </div>

        {/* Zero-Trust PoLP Ingress Barrier if Bronze is accessed by non-Data Engineer */}
        {isBronzeBlocked ? (
          <div className="bg-gradient-to-br from-rose-50/70 via-white to-amber-50/40 border-2 border-dashed border-rose-300 rounded-2xl p-7 text-left shadow-xs">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-rose-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-rose-100 border border-rose-300 flex items-center justify-center shrink-0 shadow-xs">
                  <ShieldAlert className="w-6 h-6 text-rose-600" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-bold text-rose-950">
                      Zero-Trust PoLP Ingress Barrier: Bronze (Raw Lake) Access Blocked
                    </h4>
                    <span className="text-[10px] font-mono font-bold bg-rose-600 text-white px-2 py-0.5 rounded-full uppercase">
                      HTTP 403 Forbidden
                    </span>
                  </div>
                  <p className="text-xs text-rose-700 mt-0.5 font-medium">
                    Singapore MAS Technology Risk Management (TRM) &amp; Bank Data Governance Compliance
                  </p>
                </div>
              </div>

              <div className="bg-white/80 border border-rose-200 px-3 py-1.5 rounded-xl text-right">
                <span className="text-[10px] text-slate-500 font-mono block">Principle of Least Privilege</span>
                <span className="text-xs font-bold text-slate-900 font-mono">Zero Raw PII Exposure</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-5 text-xs">
              <div className="md:col-span-2 space-y-2.5 text-slate-700">
                <p className="leading-relaxed">
                  The <strong>Medallion Raw (Bronze) tier</strong> contains uncurated, unmasked transaction telemetry
                  directly ingested from payment gateways. This includes cleartext Singapore <strong>NRIC</strong>,
                  Indian <strong>PAN</strong> numbers, and unencrypted account coordinates.
                </p>
                <p className="leading-relaxed text-slate-600">
                  In strict compliance with <strong>PoLP</strong> and regulatory mandates (MAS Notice 644 &amp; DPDP 2023),
                  direct lakehouse access to raw financial streams is restricted exclusively to authorized{' '}
                  <strong className="text-slate-900">Principal Data Platform Engineers (Alex Wong)</strong> for pipeline ingestion
                  debugging. Downstream personas must consume curated Silver or certified Gold data.
                </p>
                {accessDeniedError && (
                  <div className="bg-rose-100/70 border border-rose-200 rounded-lg p-2.5 text-[11px] font-mono text-rose-900">
                    Backend Policy Enforcement: {accessDeniedError}
                  </div>
                )}
              </div>

              <div className="bg-white border border-rose-200/80 rounded-xl p-4 space-y-2.5 shadow-2xs">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                  Current Persona Identity
                </span>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Name:</span>
                    <span className="font-semibold text-slate-900">{currentUser?.name || 'Unauthenticated'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Assigned Role:</span>
                    <span className="font-mono font-semibold text-slate-800">{currentUser?.role || 'NONE'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Clearance:</span>
                    <span className="font-mono text-slate-700">{currentUser?.clearance || 'INTERNAL'}</span>
                  </div>
                  <div className="flex justify-between items-center pt-1 border-t border-slate-100">
                    <span className="text-slate-500">Raw Clearance:</span>
                    <span className="text-[10px] font-bold text-rose-700 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded">
                      LACKS view_bronze_raw
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-rose-200 flex flex-wrap items-center justify-between gap-3">
              <span className="text-xs text-slate-600 font-medium flex items-center gap-1.5">
                <Lock className="w-4 h-4 text-rose-600" />
                Select an authorized tier to view contract-governed records:
              </span>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setActiveTier('SILVER')}
                  className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-3.5 rounded-xl text-xs transition shadow-xs"
                >
                  <span>View Silver Tier (PII Masked)</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setActiveTier('QUARANTINE')}
                  className="flex items-center space-x-2 bg-rose-600 hover:bg-rose-700 text-white font-semibold py-2 px-3.5 rounded-xl text-xs transition shadow-xs"
                >
                  <span>View Quarantine Vault</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div>
            {/* Engineer Clearance Alert if Bronze is active */}
            {activeTier === 'BRONZE' && isDataEngineer && (
              <div className="bg-amber-50 border border-amber-300 rounded-xl p-3.5 mb-4 flex items-center justify-between text-xs text-amber-900 shadow-2xs">
                <div className="flex items-center space-x-2.5">
                  <ShieldCheck className="w-4 h-4 text-amber-700 shrink-0" />
                  <div>
                    <span className="font-bold">Principal Data Platform Engineer Clearance Verified:</span>{' '}
                    <span className="text-amber-800">
                      Alex Wong (PoLP Tier-1 Clearance Active). Authorized to inspect unmasked payment streams for schema drift debugging.
                    </span>
                  </div>
                </div>
                <span className="text-[10px] font-mono bg-amber-200/70 border border-amber-400/80 px-2 py-0.5 rounded font-bold uppercase shrink-0">
                  RAW PII ACCESS GRANTED
                </span>
              </div>
            )}

            <div className="overflow-x-auto border border-slate-200 rounded-xl">
              {activeTier === 'QUARANTINE' ? (
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-[11px]">
                      <th className="py-3 px-4">Transaction ID</th>
                      <th className="py-3 px-4">Violating Field</th>
                      <th className="py-3 px-4">Quarantine Reason (Contract Failure)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono text-slate-700">
                    {tierData.map((item, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80 transition">
                        <td className="py-3 px-4 text-rose-700 font-bold">{item.transaction_id}</td>
                        <td className="py-3 px-4 text-amber-700 font-medium">{item.violating_field}</td>
                        <td className="py-3 px-4 text-slate-600 font-sans">{item.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-[11px]">
                      <th className="py-3 px-4">TX ID</th>
                      <th className="py-3 px-4">Sender Name</th>
                      <th className="py-3 px-4">Identity Doc (NRIC / PAN)</th>
                      <th className="py-3 px-4">Account</th>
                      <th className="py-3 px-4">Amount</th>
                      <th className="py-3 px-4">Rail</th>
                      <th className="py-3 px-4">Purpose</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono text-slate-700">
                    {tierData.map((item, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80 transition">
                        <td className="py-3 px-4 text-indigo-700 font-bold">{item.transaction_id}</td>
                        <td className="py-3 px-4 font-sans font-medium text-slate-900">{item.sender_name}</td>
                        <td className="py-3 px-4">
                          {activeTier === 'BRONZE' ? (
                            <span className="text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 text-[11px] font-medium">
                              {item.sender_id_doc} (Raw Cleartext)
                            </span>
                          ) : (
                            <span className="text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-bold text-[11px]">
                              {item.sender_id_doc_masked} (Pseudonymized)
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-slate-500">
                          {activeTier === 'BRONZE' ? item.sender_account : item.sender_account_masked}
                        </td>
                        <td className="py-3 px-4 font-bold text-slate-900 font-sans">
                          {item.currency === 'INR' ? '₹' : 'S$'} {Number(item.amount).toLocaleString()} {item.currency}
                        </td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-[10px] font-semibold border border-slate-200">
                            {item.payment_rail}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-sans text-slate-600">{item.purpose}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
