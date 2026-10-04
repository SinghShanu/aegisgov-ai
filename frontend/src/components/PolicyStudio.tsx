import React, { useState, useEffect } from 'react';
import {
  FileCode,
  Sparkles,
  BookOpen,
  CheckCircle2,
  Shield,
  ShieldCheck,
  AlertTriangle,
  Award,
  ArrowRight,
  Lock,
  ExternalLink
} from 'lucide-react';
import { UserPersona, DataContract } from '../types';

interface PolicyStudioProps {
  currentUser?: UserPersona;
  onNavigateToMedallion?: () => void;
}

export const PolicyStudio: React.FC<PolicyStudioProps> = ({
  currentUser,
  onNavigateToMedallion
}) => {
  const [policies, setPolicies] = useState<any[]>([]);
  const [selectedPolicy, setSelectedPolicy] = useState<any | null>(null);
  const [customText, setCustomText] = useState('');
  const [customTitle, setCustomTitle] = useState('');
  const [customAuthority, setCustomAuthority] = useState('MAS / RBI');
  const [compiledContract, setCompiledContract] = useState<DataContract | null>(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [isApproving, setIsApproving] = useState(false);

  useEffect(() => {
    fetch('/api/policies')
      .then((res) => res.json())
      .then((data) => {
        setPolicies(data);
        if (data.length > 0) {
          setSelectedPolicy(data[0]);
          setCustomTitle(data[0].title);
          setCustomAuthority(data[0].authority);
          setCustomText(data[0].raw_policy_text);
        }
      })
      .catch((err) => console.error('Failed to load policies:', err));
  }, []);

  const handleSelectPolicy = (p: any) => {
    setSelectedPolicy(p);
    setCustomTitle(p.title);
    setCustomAuthority(p.authority);
    setCustomText(p.raw_policy_text);
    setCompiledContract(null);
  };

  const handleCompile = async () => {
    setIsCompiling(true);
    try {
      const res = await fetch('/api/policies/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          policy_title: customTitle,
          authority: customAuthority,
          policy_text: customText
        })
      });
      const data = await res.json();
      setCompiledContract(data);
    } catch (err) {
      console.error('Compilation failed:', err);
    } finally {
      setIsCompiling(false);
    }
  };

  const handleApproveContract = async () => {
    if (!compiledContract || !currentUser) return;
    setIsApproving(true);
    try {
      const res = await fetch(`/api/policies/contracts/${compiledContract.contract_id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reviewer_id: currentUser.user_id,
          reviewer_name: currentUser.name,
          reviewer_role: currentUser.role,
          remarks: `Approved for Medallion pipeline enforcement under ${compiledContract.governing_regulation}`
        })
      });
      if (res.ok) {
        const updated = await res.json();
        setCompiledContract(updated);
      }
    } catch (err) {
      console.error('Approval failed:', err);
    } finally {
      setIsApproving(false);
    }
  };

  const isGovernanceOfficer =
    currentUser?.role === 'COMPLIANCE_OFFICER' || currentUser?.role === 'RISK_OFFICER';

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FileCode className="w-5 h-5 text-indigo-600" />
            Policy-as-Code Studio (Agent 1: Regulatory Transpiler)
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Translates natural language regulatory policies into machine-executable JSON data contracts, governing the Medallion Lakehouse lifecycle.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono bg-indigo-50 text-indigo-700 border border-indigo-100 px-3 py-1.5 rounded-xl font-medium">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <span>Powered by Gemini 2.0 Pro</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Policy Selector & Editor (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3 flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-indigo-600" />
              <span>Standard JAPAC BFSI Regulatory Policies</span>
            </h3>
            <div className="space-y-2.5">
              {policies.map((p, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSelectPolicy(p)}
                  className={`p-3.5 rounded-xl border transition cursor-pointer text-left ${
                    selectedPolicy?.policy_id === p.policy_id
                      ? 'bg-indigo-50/60 border-indigo-500 ring-2 ring-indigo-500/20 shadow-sm'
                      : 'bg-slate-50 border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs font-bold text-slate-900 mb-1">
                    <span>{p.title}</span>
                    <span className="text-[10px] font-mono text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded font-medium">
                      {p.jurisdiction}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed">
                    {p.summary}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Policy Text Editor */}
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
            <div>
              <label className="text-xs font-bold text-slate-800 mb-1.5 block">
                Policy Document Text (Natural Language):
              </label>
              <textarea
                rows={7}
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-sans leading-relaxed"
              />
            </div>
            <button
              disabled={isCompiling || !customText.trim()}
              onClick={handleCompile}
              className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl text-xs transition shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isCompiling ? 'Synthesizing Policy-as-Code...' : 'Compile to Machine Data Contract'}</span>
            </button>
          </div>
        </div>

        {/* Right: Compiled Policy-as-Code JSON Contract & Lifecycle Enforcement (6 cols) */}
        <div className="lg:col-span-6 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <FileCode className="w-4 h-4 text-emerald-600" />
                <span>Compiled Machine-Executable Contract</span>
              </h3>
              {compiledContract && (
                <span
                  className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full font-bold border ${
                    compiledContract.status === 'ACTIVE_ENFORCING'
                      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border-amber-200 animate-pulse'
                  }`}
                >
                  {compiledContract.status === 'ACTIVE_ENFORCING'
                    ? '● ACTIVE & ENFORCING'
                    : '⏳ PENDING GOVERNANCE APPROVAL'}
                </span>
              )}
            </div>

            {compiledContract ? (
              <div className="space-y-4">
                {/* Contract Metadata Card */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-slate-500 font-medium">Contract ID:</span>{' '}
                      <span className="font-mono text-indigo-700 font-bold">{compiledContract.contract_id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500 font-medium">Target Tier:</span>{' '}
                      <span className="font-mono text-emerald-700 font-bold">{compiledContract.target_tier}</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-slate-500 font-medium">Governing Regulation:</span>{' '}
                    <span className="text-slate-800 font-medium">{compiledContract.governing_regulation}</span>
                  </div>
                </div>

                {/* ------------------------------------------------------------- */}
                {/* Dual-Persona Governance Review & Approval Gate */}
                {/* ------------------------------------------------------------- */}
                {compiledContract.status === 'PENDING_APPROVAL' && (
                  <div className="bg-amber-50/70 border border-amber-200/90 rounded-xl p-4 space-y-3">
                    <div className="flex items-start gap-2.5">
                      <Shield className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-xs font-bold text-amber-900">
                          SOC 2 CC8.1 Change Management & Data Governance Signoff
                        </h4>
                        <p className="text-[11px] text-amber-800 mt-0.5 leading-relaxed">
                          Newly synthesized data contracts require dual-signatory approval from Compliance or Risk before deployment into the live Medallion pipeline.
                        </p>
                      </div>
                    </div>

                    {isGovernanceOfficer ? (
                      <div className="pt-1">
                        <button
                          disabled={isApproving}
                          onClick={handleApproveContract}
                          className="w-full flex items-center justify-center space-x-2 bg-amber-600 hover:bg-amber-700 text-white font-bold py-2.5 px-4 rounded-xl text-xs transition shadow-xs disabled:opacity-50"
                        >
                          <ShieldCheck className="w-4 h-4" />
                          <span>
                            {isApproving
                              ? 'Deploying Contract to Pipeline...'
                              : `Approve & Deploy Contract as ${currentUser?.name}`}
                          </span>
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 p-2.5 rounded-lg bg-white/80 border border-amber-200 text-xs text-amber-900">
                        <Lock className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                        <span className="text-[11px]">
                          Approval restricted to <strong>Compliance Officer</strong> (Priya Sharma) or{' '}
                          <strong>Risk Officer</strong> (Kenji Sato). Current role ({currentUser?.role}) cannot deploy contracts.
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* ------------------------------------------------------------- */}
                {/* Interactive 4-Stage Lifecycle Enforcement Stepper (When Active) */}
                {/* ------------------------------------------------------------- */}
                {compiledContract.status === 'ACTIVE_ENFORCING' && (
                  <div className="bg-emerald-50/40 border border-emerald-200/90 rounded-xl p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-emerald-600" />
                        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                          Data Management Lifecycle Enforcement
                        </h4>
                      </div>
                      <span className="text-[10px] font-mono text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded font-semibold">
                        LIVE ON MEDALLION PIPELINE
                      </span>
                    </div>

                    {/* 4-Stage Visual Stepper */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1">
                      {/* Step 1: Bronze Ingestion Gate */}
                      <div className="bg-white border border-slate-200 rounded-lg p-2.5 text-left">
                        <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Stage 1</div>
                        <div className="text-xs font-bold text-slate-800 mt-0.5">Bronze Gate</div>
                        <div className="text-[11px] font-bold text-indigo-600 mt-1">36 Records</div>
                        <div className="text-[9px] text-slate-500 mt-0.5">Schema adherence verified</div>
                      </div>

                      {/* Step 2: Silver Masking & Tokenization */}
                      <div className="bg-white border border-slate-200 rounded-lg p-2.5 text-left">
                        <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Stage 2</div>
                        <div className="text-xs font-bold text-slate-800 mt-0.5">Silver Masking</div>
                        <div className="text-[11px] font-bold text-emerald-600 mt-1">34 Promoted</div>
                        <div className="text-[9px] text-slate-500 mt-0.5">NRIC/PAN vault tokenized</div>
                      </div>

                      {/* Step 3: Quarantine Isolation */}
                      <div className="bg-white border border-slate-200 rounded-lg p-2.5 text-left">
                        <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Stage 3</div>
                        <div className="text-xs font-bold text-slate-800 mt-0.5">Quarantine</div>
                        <div className="text-[11px] font-bold text-amber-600 mt-1">2 Quarantined</div>
                        <div className="text-[9px] text-slate-500 mt-0.5">Contract violations blocked</div>
                      </div>

                      {/* Step 4: Gold Certification */}
                      <div className="bg-white border border-slate-200 rounded-lg p-2.5 text-left">
                        <div className="text-[10px] uppercase font-bold text-slate-400 font-mono">Stage 4</div>
                        <div className="text-xs font-bold text-slate-800 mt-0.5">Gold Certified</div>
                        <div className="text-[11px] font-bold text-emerald-600 mt-1">94.4% Health</div>
                        <div className="text-[9px] text-slate-500 mt-0.5">HMAC audit sealed</div>
                      </div>
                    </div>

                    {/* Attestation signoff & Medallion Link */}
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pt-2 border-t border-emerald-100 text-xs">
                      <span className="text-[11px] text-slate-600">
                        Deployed by <strong className="text-slate-800">{compiledContract.approved_by}</strong> at{' '}
                        <span className="font-mono text-[10px] text-slate-500">{compiledContract.approved_at}</span>
                      </span>

                      {onNavigateToMedallion && (
                        <button
                          onClick={onNavigateToMedallion}
                          className="flex items-center gap-1 text-xs font-bold text-indigo-700 hover:text-indigo-900 transition"
                        >
                          <span>View in Medallion Lineage</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {/* Enforced Column Rules */}
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Enforced Column Rules ({compiledContract.rules?.length || 0})
                  </h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {compiledContract.rules?.map((rule: any, i: number) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                        <div className="flex items-center justify-between font-mono">
                          <span className="text-indigo-700 font-bold">{rule.column_name}</span>
                          <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-semibold">
                            {rule.masking_strategy}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-600 mt-1">
                          {rule.description}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Raw JSON Schema Payload */}
                <div>
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Machine-Readable Contract Schema (JSON)
                  </h4>
                  <pre className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 text-[11px] font-mono text-emerald-400 overflow-x-auto max-h-36">
                    {JSON.stringify(compiledContract, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-24 text-center text-slate-400">
                <FileCode className="w-8 h-8 text-slate-300 mb-2" />
                <p className="text-xs font-medium text-slate-500 max-w-xs">
                  Click "Compile to Machine Data Contract" on the left to synthesize machine-executable rules.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
