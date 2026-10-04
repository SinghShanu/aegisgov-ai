import React, { useState, useEffect } from 'react';
import { ShieldAlert, ShieldCheck, Zap, AlertTriangle, Radio, Activity } from 'lucide-react';

export const ThreatRadar: React.FC = () => {
  const [radarData, setRadarData] = useState<any | null>(null);

  const fetchRadar = () => {
    fetch('/api/audit/threat-radar')
      .then(res => res.json())
      .then(data => setRadarData(data))
      .catch(err => console.error('Failed to load radar data:', err));
  };

  useEffect(() => {
    fetchRadar();
    const interval = setInterval(fetchRadar, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Radio className="w-5 h-5 text-indigo-600" />
            AI Safety Harness Threat Radar & Telemetry
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Continuous detection of adversarial prompt injections, jailbreak vectors, context poisoning, and high-frequency bot probing.
          </p>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-xl font-medium">
          <Activity className="w-4 h-4 text-emerald-600" />
          <span>Status: ALL DEFENSES ACTIVE</span>
        </div>
      </div>

      {radarData && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Critical Attacks Intercepted</span>
            <div className="text-2xl font-bold text-rose-600 font-mono mt-1">
              {radarData.attacks_blocked_count}
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">
              Jailbreak & Injection Mitigations
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">HITL Escalations Triggered</span>
            <div className="text-2xl font-bold text-amber-600 font-mono mt-1">
              {radarData.hitl_escalations_count}
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">
              Four-Eyes Boundary Holds
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Compliant AI Interactions</span>
            <div className="text-2xl font-bold text-emerald-600 font-mono mt-1">
              {radarData.authorized_transactions_count}
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-1 block">
              Verified under RBAC & PoLP
            </span>
          </div>
        </div>
      )}

      {/* Active Defense Grid */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-4">
          Autonomous Enterprise Safety Harness Perimeters
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 mb-1.5">
              <ShieldAlert className="w-4 h-4 text-rose-600" />
              <span>Prompt Injection Guard</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Mitigates direct system overrides, roleplay exploits (DAN), and indirect prompt injection embedded in financial records.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 mb-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>JAPAC PII Dynamic Tokenizer</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Detects Singapore NRIC/FIN and Indian PAN/Aadhaar in real time, converting cleartext into ephemeral synthetic vault tokens.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 mb-1.5">
              <Zap className="w-4 h-4 text-amber-500" />
              <span>Financial Circuit Breaker</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Deterministic gate pausing transactions exceeding S$ 10,000 or ₹ 5 Lakhs for mandatory dual-human authorization.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 mb-1.5">
              <AlertTriangle className="w-4 h-4 text-indigo-600" />
              <span>Context Poisoning Filter</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Monitors prompt delimiters, token density anomalies, and malicious control characters attempting to subvert LLM attention.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 mb-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
              <span>MAS FEAT Grounding Verifier</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Suppresses model hallucinations by cross-checking numeric claims against verified Gold Lakehouse data prior to egress.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-900 mb-1.5">
              <ShieldAlert className="w-4 h-4 text-purple-600" />
              <span>Cryptographic Secret Blocker</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">
              Scans outgoing agent tokens to intercept accidental leakage of GCP API keys, database connection strings, or RSA keys.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
