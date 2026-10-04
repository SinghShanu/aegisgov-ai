import React, { useState, useEffect } from 'react';
import { GCPArchitectureOverview, GCPServiceDetail } from '../types';
import { 
  Cloud, 
  Brain, 
  ShieldCheck, 
  Activity, 
  Database, 
  Server, 
  Key, 
  Lock, 
  CheckCircle2, 
  ExternalLink, 
  Terminal, 
  FileText,
  Zap,
  Globe2
} from 'lucide-react';

export const GCPArchitectureMatrix: React.FC = () => {
  const [overview, setOverview] = useState<GCPArchitectureOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeMode, setActiveMode] = useState<'local' | 'cloud'>('local');

  const fetchArchitecture = () => {
    fetch('/api/gcp/architecture')
      .then(res => res.json())
      .then(data => {
        setOverview(data);
        setActiveMode(data.gcp_mode as 'local' | 'cloud');
      })
      .catch(err => console.error('Failed to load GCP architecture:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchArchitecture();
  }, []);

  const handleModeSwitch = async (mode: 'local' | 'cloud') => {
    setActiveMode(mode);
    await fetch('/api/gcp/mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode })
    });
    fetchArchitecture();
  };

  const getServiceIcon = (name: string) => {
    switch (name) {
      case 'Brain': return <Brain className="w-5 h-5 text-indigo-600" />;
      case 'ShieldCheck': return <ShieldCheck className="w-5 h-5 text-emerald-600" />;
      case 'Activity': return <Activity className="w-5 h-5 text-amber-600" />;
      case 'Database': return <Database className="w-5 h-5 text-cyan-600" />;
      case 'Server': return <Server className="w-5 h-5 text-violet-600" />;
      case 'Key': return <Key className="w-5 h-5 text-rose-600" />;
      case 'Lock': return <Lock className="w-5 h-5 text-blue-600" />;
      default: return <Cloud className="w-5 h-5 text-slate-600" />;
    }
  };

  if (loading || !overview) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
                <Cloud className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">
                Google Cloud Platform & Agentic AI Architecture Matrix
              </h2>
              <span className="text-xs font-semibold bg-emerald-50 text-emerald-700 px-2.5 py-0.5 rounded-full border border-emerald-200">
                7 Services Mapped
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1.5 max-w-3xl">
              End-to-end reference architecture aligning Google Cloud enterprise infrastructure with MAS (Singapore), RBI (India), and SOC 2 Type II compliance controls for Tier-1 JAPAC banks.
            </p>
          </div>

          {/* Mode Switcher & Project Pills */}
          <div className="flex flex-wrap items-center gap-2.5">
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
              <button
                onClick={() => handleModeSwitch('local')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  activeMode === 'local'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                Local Emulated Mode
              </button>
              <button
                onClick={() => handleModeSwitch('cloud')}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  activeMode === 'cloud'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                GCP Cloud Native
              </button>
            </div>

            <div className="text-right hidden sm:block border-l border-slate-200 pl-3">
              <div className="text-[11px] font-mono text-slate-500">
                GCP Project: <span className="font-bold text-slate-800">{overview.project_id}</span>
              </div>
              <div className="text-[11px] font-mono text-slate-500">
                Region: <span className="font-bold text-indigo-600">{overview.region}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {overview.services.map((svc, idx) => (
          <div
            key={idx}
            className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-indigo-200 transition flex flex-col justify-between"
          >
            <div>
              {/* Card Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-center">
                  {getServiceIcon(svc.icon_name)}
                </div>
                <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                  {svc.category}
                </span>
              </div>

              {/* Service Title & GCP Product */}
              <h3 className="text-sm font-bold text-slate-900 leading-snug">
                {svc.service_name}
              </h3>
              <div className="text-xs font-semibold text-indigo-600 mt-0.5">
                {svc.gcp_product}
              </div>

              {/* Problem Addressed */}
              <div className="mt-3.5 pt-3 border-t border-slate-100">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Banking Problem Addressed
                </div>
                <p className="text-xs text-slate-700 mt-1 leading-relaxed">
                  {svc.problem_addressed}
                </p>
              </div>

              {/* Architecture Role */}
              <div className="mt-3">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Architecture Role
                </div>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {svc.architecture_role}
                </p>
              </div>
            </div>

            {/* Footer Regulatory Tag & Status */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex flex-col space-y-2">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-slate-500">Mode:</span>
                <span className="font-semibold text-slate-800 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                  {svc.operational_mode}
                </span>
              </div>
              <div className="text-[11px] text-slate-500 bg-amber-50/60 border border-amber-200/60 p-2 rounded-lg">
                <span className="font-bold text-amber-800">Compliance: </span>
                <span className="text-amber-900">{svc.regulatory_relevance}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Executive Finance ROI & Regulatory Impact Matrix */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center space-x-2.5 mb-4">
          <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              Executive Finance ROI & High-Impact Business Outcomes
            </h3>
            <p className="text-xs text-slate-500">
              How unified Data & AI Governance translates directly to bank OpEx reduction, fraud mitigation, and speed-to-market.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-rose-600 bg-rose-50 px-2 py-0.5 rounded w-fit border border-rose-200 mb-2">
              Fraud & Mule Ring ROI
            </div>
            <div className="text-xs font-bold text-slate-900">
              Cross-Rail Scam Interception
            </div>
            <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Eliminates 75% of manual Level-1 AML false positives (~$2.8M OpEx savings) and prevents direct scam restitution liability under Singapore's Shared Responsibility Framework (SRF).
            </p>
            <div className="mt-3 pt-2 border-t border-slate-200/60 text-[11px] font-medium text-slate-500">
              GCP: Cloud DLP + BigQuery Quarantine + Vertex AI Ingress
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded w-fit border border-amber-200 mb-2">
              Lending Turnaround ROI
            </div>
            <div className="text-xs font-bold text-slate-900">
              45-Second SME Credit Decisioning
            </div>
            <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Accelerates commercial loan decisioning from 5 business days to 45 seconds while cutting default rates by 22% via multi-rail cash flow verification under RBI Digital Lending rules.
            </p>
            <div className="mt-3 pt-2 border-t border-slate-200/60 text-[11px] font-medium text-slate-500">
              GCP: Gemini 2.0 Grounding + BigQuery Gold + Circuit Breaker
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
            <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded w-fit border border-indigo-200 mb-2">
              Fiduciary Advisory ROI
            </div>
            <div className="text-xs font-bold text-slate-900">
              3x Wealth Advisor Capacity
            </div>
            <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
              Empowers certified wealth advisors to manage 3x more portfolios with automated, pre-cleared rebalancing notes and 100% elimination of mis-selling fines under MAS FEAT principles.
            </p>
            <div className="mt-3 pt-2 border-t border-slate-200/60 text-[11px] font-medium text-slate-500">
              GCP: Vertex AI Agent Builder + Secret Manager KMS Ledger
            </div>
          </div>
        </div>
      </div>

      {/* Cloud Run Deployment & Architecture Commands Section */}
      <div className="bg-slate-900 text-slate-100 rounded-2xl p-6 shadow-sm border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2 text-sm font-bold text-white">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>Cloud Native Deployment Commands (Singapore Region)</span>
          </div>
          <span className="text-xs text-emerald-400 font-mono">asia-southeast1</span>
        </div>
        <div className="space-y-3 font-mono text-xs">
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80 overflow-x-auto text-slate-300">
            <span className="text-indigo-400"># 1. Deploy Container to Google Cloud Run with Free Tier Safety Quotas</span><br />
            gcloud run deploy aegisgov-ai \<br />
            &nbsp;&nbsp;--source . \<br />
            &nbsp;&nbsp;--region asia-southeast1 \<br />
            &nbsp;&nbsp;--platform managed \<br />
            &nbsp;&nbsp;--allow-unauthenticated \<br />
            &nbsp;&nbsp;--max-instances 2 \<br />
            &nbsp;&nbsp;--set-env-vars BASE_CURRENCY=SGD,ENVIRONMENT=production,GCP_MODE=cloud
          </div>
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80 overflow-x-auto text-slate-300">
            <span className="text-indigo-400"># 2. Provision Pub/Sub Streaming Rails Topic</span><br />
            gcloud pubsub topics create japac-rail-transactions --message-retention-duration=1d
          </div>
        </div>
      </div>
    </div>
  );
};
