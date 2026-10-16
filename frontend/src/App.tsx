import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { HarnessPlayground } from './components/HarnessPlayground';
import { MedallionLineage } from './components/MedallionLineage';
import { PolicyStudio } from './components/PolicyStudio';
import { ThreatRadar } from './components/ThreatRadar';
import { AuditLedger } from './components/AuditLedger';
import { HITLApprovalCenter } from './components/HITLApprovalCenter';
import { SOC2AuditStudio } from './components/SOC2AuditStudio';
import { GCPArchitectureMatrix } from './components/GCPArchitectureMatrix';
import { RegressionGuardianStudio } from './components/RegressionGuardianStudio';
import { UserPersona, HITLTicket, StreamStatus } from './types';
import {
  ShieldCheck,
  Database,
  Award,
  FlaskConical,
  Bot,
  Radio,
  FileCode,
  History,
  Cloud,
  ChevronRight
} from 'lucide-react';

type MainConsole = 'sentinel_defense' | 'policy_lakehouse' | 'compliance_cloud' | 'regression';
type SentinelSubView = 'sentinel' | 'threats';
type LakehouseSubView = 'policies' | 'medallion';
type ComplianceSubView = 'soc2' | 'architecture' | 'audit';

export const App: React.FC = () => {
  const [personas, setPersonas] = useState<Record<string, UserPersona>>({});
  const [selectedPersonaKey, setSelectedPersonaKey] = useState<string>('wealth_advisor');
  const [activeConsole, setActiveConsole] = useState<MainConsole>('sentinel_defense');
  const [sentinelSubView, setSentinelSubView] = useState<SentinelSubView>('sentinel');
  const [lakehouseSubView, setLakehouseSubView] = useState<LakehouseSubView>('policies');
  const [complianceSubView, setComplianceSubView] = useState<ComplianceSubView>('soc2');

  const [hitlTickets, setHitlTickets] = useState<HITLTicket[]>([]);
  const [isHitlOpen, setIsHitlOpen] = useState(false);
  const [streamStatus, setStreamStatus] = useState<StreamStatus | null>(null);
  const [burstLoading, setBurstLoading] = useState(false);

  // Fetch Personas
  useEffect(() => {
    fetch('/api/harness/personas')
      .then((res) => res.json())
      .then((data) => setPersonas(data))
      .catch((err) => console.error('Failed to load personas:', err));
  }, []);

  // Fetch HITL Tickets
  const refreshTickets = () => {
    fetch('/api/hitl/tickets')
      .then((res) => res.json())
      .then((data) => setHitlTickets(data))
      .catch((err) => console.error('Failed to load tickets:', err));
  };

  // Fetch Live Rail Stream Status
  const refreshStreamStatus = async () => {
    try {
      const res = await fetch('/api/stream/status');
      if (res.ok) {
        const data = await res.json();
        setStreamStatus(data);
      }
    } catch (err) {
      console.error('Failed to load stream status:', err);
    }
  };

  useEffect(() => {
    refreshTickets();
    refreshStreamStatus();
    const interval = setInterval(() => {
      refreshTickets();
      refreshStreamStatus();
    }, 3500);
    return () => clearInterval(interval);
  }, []);

  const handleToggleStream = async () => {
    if (!streamStatus) return;
    const endpoint = streamStatus.is_running ? '/api/stream/stop' : '/api/stream/start';
    await fetch(endpoint, { method: 'POST' });
    await refreshStreamStatus();
  };

  const handleTriggerBurst = async () => {
    setBurstLoading(true);
    try {
      await fetch('/api/stream/burst', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: 10 })
      });
      await refreshStreamStatus();
      await refreshTickets();
    } finally {
      setBurstLoading(false);
    }
  };

  const handleResolveTicket = async (ticketId: string, decision: 'APPROVED' | 'REJECTED', remarks: string) => {
    const currentPersona = personas[selectedPersonaKey];
    if (!currentPersona) return;

    await fetch('/api/hitl/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticket_id: ticketId,
        reviewer_id: currentPersona.user_id,
        reviewer_name: currentPersona.name,
        reviewer_role: currentPersona.role,
        decision,
        remarks
      })
    });
    await refreshTickets();
  };

  const currentPersona = personas[selectedPersonaKey] || {
    user_id: 'usr_default',
    name: 'Wealth Advisor',
    role: 'WEALTH_ADVISOR',
    clearance: 'CONFIDENTIAL',
    jurisdiction: 'SG',
    allowed_actions: [],
    max_transaction_limit_sgd: 10000,
    max_transaction_limit_inr: 500000,
    can_approve_hitl: false,
    session_token: 'tok_default',
    token_ttl_seconds: 3600
  };

  const pendingHitlCount = hitlTickets.filter((t) => t.status === 'PENDING').length;

  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAFC] text-slate-800 font-sans">
      <Header
        personas={personas}
        selectedPersonaKey={selectedPersonaKey}
        onSelectPersona={setSelectedPersonaKey}
        pendingHitlCount={pendingHitlCount}
        onOpenHitlCenter={() => setIsHitlOpen(true)}
        streamStatus={streamStatus}
        onToggleStream={handleToggleStream}
        onTriggerBurst={handleTriggerBurst}
        burstLoading={burstLoading}
      />

      {/* Main 4-Console Navigation Strip */}
      <div className="border-b border-slate-200 bg-white px-6 py-2.5 sticky top-[69px] z-30 shadow-xs">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <nav className="flex items-center space-x-2.5 overflow-x-auto py-0.5">
            {/* Console 1 */}
            <button
              onClick={() => setActiveConsole('sentinel_defense')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeConsole === 'sentinel_defense'
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <ShieldCheck className="w-4 h-4 text-indigo-600" />
              <span>Financial Sentinel & Live Defense</span>
            </button>

            {/* Console 2 */}
            <button
              onClick={() => setActiveConsole('policy_lakehouse')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeConsole === 'policy_lakehouse'
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Database className="w-4 h-4 text-indigo-600" />
              <span>Policy-as-Code & Lakehouse</span>
            </button>

            {/* Console 3 */}
            <button
              onClick={() => setActiveConsole('compliance_cloud')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeConsole === 'compliance_cloud'
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Award className="w-4 h-4 text-indigo-600" />
              <span>Compliance & Cloud Matrix</span>
            </button>

            {/* Console 4 */}
            <button
              onClick={() => setActiveConsole('regression')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition ${
                activeConsole === 'regression'
                  ? 'bg-indigo-50 text-indigo-700 border border-indigo-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <FlaskConical className="w-4 h-4 text-indigo-600" />
              <span>Regression Guardian</span>
            </button>
          </nav>

          <div className="hidden lg:flex items-center space-x-3 text-xs font-mono text-slate-600">
            <span className="flex items-center gap-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              MAS & RBI Rails: Active
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Workspace with Generous Spacing */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">
        {/* ========================================================================= */}
        {/* CONSOLE 1: Financial Sentinel & Live Defense Hub */}
        {/* ========================================================================= */}
        {activeConsole === 'sentinel_defense' && (
          <div>
            {/* Sub-view Navigation Pill Bar */}
            <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-1.5 mb-6 shadow-2xs">
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => setSentinelSubView('sentinel')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    sentinelSubView === 'sentinel'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Bot className="w-3.5 h-3.5" />
                  <span>Aegis Financial Sentinel & 5-Stage Harness</span>
                </button>

                <button
                  onClick={() => setSentinelSubView('threats')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    sentinelSubView === 'threats'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Radio className="w-3.5 h-3.5" />
                  <span>Live Threat Radar & Quarantined Scams</span>
                </button>
              </div>

              <div className="hidden md:flex items-center text-[11px] text-slate-500 font-mono pr-2">
                <span>Real-time Ingress Defense • PoLP Gating • Four-Eyes Circuit Breaker</span>
              </div>
            </div>

            {sentinelSubView === 'sentinel' && (
              <HarnessPlayground
                currentUser={currentPersona}
                selectedPersonaKey={selectedPersonaKey}
                onRefreshTickets={refreshTickets}
              />
            )}
            {sentinelSubView === 'threats' && <ThreatRadar />}
          </div>
        )}

        {/* ========================================================================= */}
        {/* CONSOLE 2: Policy-as-Code & Medallion Lakehouse Hub */}
        {/* ========================================================================= */}
        {activeConsole === 'policy_lakehouse' && (
          <div>
            {/* Sub-view Navigation Pill Bar */}
            <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-1.5 mb-6 shadow-2xs">
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => setLakehouseSubView('policies')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    lakehouseSubView === 'policies'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <FileCode className="w-3.5 h-3.5" />
                  <span>Policy-as-Code Studio (Gemini Compiler)</span>
                </button>

                <button
                  onClick={() => setLakehouseSubView('medallion')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    lakehouseSubView === 'medallion'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Database className="w-3.5 h-3.5" />
                  <span>Medallion Lakehouse Lineage (Bronze → Silver → Gold)</span>
                </button>
              </div>

              <div className="hidden md:flex items-center text-[11px] text-slate-500 font-mono pr-2">
                <span>MAS & RBI Machine-Readable Data Contracts • PII Tokenization</span>
              </div>
            </div>

            {lakehouseSubView === 'policies' && (
              <PolicyStudio
                currentUser={currentPersona}
                onNavigateToMedallion={() => setLakehouseSubView('medallion')}
              />
            )}
            {lakehouseSubView === 'medallion' && (
              <MedallionLineage
                currentUser={currentPersona}
                selectedPersonaKey={selectedPersonaKey}
              />
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* CONSOLE 3: Compliance & Cloud Matrix Hub */}
        {/* ========================================================================= */}
        {activeConsole === 'compliance_cloud' && (
          <div>
            {/* Sub-view Navigation Pill Bar */}
            <div className="flex items-center justify-between bg-white border border-slate-200 rounded-xl p-1.5 mb-6 shadow-2xs">
              <div className="flex items-center space-x-1.5">
                <button
                  onClick={() => setComplianceSubView('soc2')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    complianceSubView === 'soc2'
                      ? 'bg-amber-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Award className="w-3.5 h-3.5" />
                  <span>SOC 2 & JAPAC Evidence Studio</span>
                </button>

                <button
                  onClick={() => setComplianceSubView('architecture')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    complianceSubView === 'architecture'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Cloud className="w-3.5 h-3.5" />
                  <span>Google Cloud 7-Service Architecture & ROI</span>
                </button>

                <button
                  onClick={() => setComplianceSubView('audit')}
                  className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                    complianceSubView === 'audit'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <History className="w-3.5 h-3.5" />
                  <span>Cryptographic Audit Ledger</span>
                </button>
              </div>

              <div className="hidden md:flex items-center text-[11px] text-slate-500 font-mono pr-2">
                <span>Trust Services Criteria • HMAC SHA-256 Ledger • Cloud Parity</span>
              </div>
            </div>

            {complianceSubView === 'soc2' && <SOC2AuditStudio />}
            {complianceSubView === 'architecture' && <GCPArchitectureMatrix />}
            {complianceSubView === 'audit' && <AuditLedger />}
          </div>
        )}

        {/* ========================================================================= */}
        {/* CONSOLE 4: Regression Guardian Studio */}
        {/* ========================================================================= */}
        {activeConsole === 'regression' && (
          <div>
            <RegressionGuardianStudio />
          </div>
        )}
      </main>

      {/* HITL Modal Drawer */}
      <HITLApprovalCenter
        isOpen={isHitlOpen}
        onClose={() => setIsHitlOpen(false)}
        tickets={hitlTickets}
        currentUser={currentPersona}
        onResolveTicket={handleResolveTicket}
      />
    </div>
  );
};
