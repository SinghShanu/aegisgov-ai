import React from 'react';
import { Shield, ShieldAlert, ChevronDown, Globe2, Play, Pause, Zap, RotateCcw } from 'lucide-react';
import { UserPersona, StreamStatus } from '../types';

interface HeaderProps {
  personas: Record<string, UserPersona>;
  selectedPersonaKey: string;
  onSelectPersona: (key: string) => void;
  pendingHitlCount: number;
  onOpenHitlCenter: () => void;
  streamStatus?: StreamStatus | null;
  onToggleStream?: () => void;
  onTriggerBurst?: () => void;
  burstLoading?: boolean;
  onResetDemo?: () => void;
  isResetting?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  personas,
  selectedPersonaKey,
  onSelectPersona,
  pendingHitlCount,
  onOpenHitlCenter,
  streamStatus,
  onToggleStream,
  onTriggerBurst,
  burstLoading = false,
  onResetDemo,
  isResetting = false
}) => {
  const currentPersona = personas[selectedPersonaKey];

  // Clean persona title and role labels
  const rawName = currentPersona?.name || 'User';
  const cleanName = rawName.includes('(') ? rawName.split('(')[0].trim() : rawName;
  const cleanRole = rawName.includes('(')
    ? rawName.split('(')[1].replace(')', '').trim()
    : (currentPersona?.role ? currentPersona.role.replace('_', ' ') : 'Specialist');

  // Derive user initials for the avatar badge
  const initials = cleanName
    .split(' ')
    .filter(Boolean)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || 'U';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 px-6 py-3.5 shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-6">
        {/* Brand & Platform Lockup */}
        <div className="flex items-center gap-3.5 shrink-0">
          <img
            src="/aegisgov_team_logo.jpg"
            alt="AegisGov AI Emblem"
            className="w-9 h-9 rounded-xl object-contain bg-white border border-slate-200/80 p-0.5 shadow-xs shrink-0 ring-1 ring-slate-100"
          />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-slate-900 tracking-tight">
                AegisGov <span className="text-indigo-600">AI</span>
              </span>
              <span className="text-[10px] font-semibold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md border border-slate-200 tracking-tight uppercase">
                Enterprise BFSI
              </span>
            </div>
            <p className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
              <Globe2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span>JAPAC Policy-as-Code & Multi-Agent Safety Harness (MAS & RBI)</span>
            </p>
          </div>
        </div>

        {/* Demarcated Control Islands (Telemetry Capsule | HITL Queue | User Identity) */}
        <div className="flex items-center gap-3 md:gap-3.5">
          {/* Zone A: Live Rails & Streaming Telemetry Capsule */}
          {streamStatus && (
            <div className="flex items-center bg-slate-50 border border-slate-200/90 rounded-xl p-1 shadow-2xs">
              <div className="flex items-center gap-1.5 px-2.5 py-1">
                <span className="relative flex h-2 w-2">
                  {streamStatus.is_running && (
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  )}
                  <span
                    className={`relative inline-flex rounded-full h-2 w-2 ${
                      streamStatus.is_running ? 'bg-emerald-500' : 'bg-slate-400'
                    }`}
                  />
                </span>
                <span className="text-[11px] font-semibold text-slate-700">
                  {streamStatus.is_running ? 'Live Rails' : 'Stream Paused'}
                </span>
                <span className="text-[10px] text-slate-500 font-mono hidden xl:inline">
                  ({streamStatus.total_generated} tx)
                </span>
              </div>

              {/* Internal subtle divider */}
              <div className="h-4 w-px bg-slate-200 mx-0.5" />

              {/* Start / Pause Button */}
              {onToggleStream && (
                <button
                  onClick={onToggleStream}
                  title={streamStatus.is_running ? 'Pause streaming ingestion' : 'Resume streaming ingestion'}
                  className={`p-1.5 rounded-lg text-xs font-semibold transition ${
                    streamStatus.is_running
                      ? 'bg-amber-100 text-amber-800 hover:bg-amber-200'
                      : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-2xs'
                  }`}
                >
                  {streamStatus.is_running ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                </button>
              )}

              {/* Burst Button */}
              {onTriggerBurst && (
                <button
                  onClick={onTriggerBurst}
                  disabled={burstLoading}
                  title="Inject burst of 10 certified JAPAC transactions"
                  className="flex items-center gap-1 px-2 py-1 ml-0.5 rounded-lg text-[11px] font-bold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200/60 transition disabled:opacity-50"
                >
                  <Zap className="w-3 h-3 text-indigo-600" />
                  <span>+10</span>
                </button>
              )}
            </div>
          )}

          {/* Vertical Separator */}
          <div className="h-6 w-px bg-slate-200 hidden sm:block" />

          {/* Zone B: HITL Pending Approvals Notification Pill */}
          <button
            onClick={onOpenHitlCenter}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition border shadow-2xs ${
              pendingHitlCount > 0
                ? 'bg-amber-50/90 border-amber-300 text-amber-900 hover:bg-amber-100'
                : 'bg-slate-50 border-slate-200/90 text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
            title="Open Human-In-The-Loop (HITL) Four-Eyes Approval Center"
          >
            <div className="relative">
              <ShieldAlert className={`w-4 h-4 ${pendingHitlCount > 0 ? 'text-amber-600' : 'text-slate-400'}`} />
              {pendingHitlCount > 0 && (
                <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-amber-500 animate-ping" />
              )}
            </div>
            <span className="hidden sm:inline">HITL Approvals</span>
            <span
              className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold font-mono ${
                pendingHitlCount > 0 ? 'bg-amber-500 text-white' : 'bg-slate-200 text-slate-600'
              }`}
            >
              {pendingHitlCount}
            </span>
          </button>

          {/* Reset Demo State Button */}
          {onResetDemo && (
            <button
              onClick={onResetDemo}
              disabled={isResetting}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold bg-rose-50/90 hover:bg-rose-100 text-rose-700 border border-rose-200/90 transition shadow-2xs disabled:opacity-50"
              title="Reset entire demo state (clears executed orders, restores initial tickets and audit ledger)"
            >
              <RotateCcw className={`w-3.5 h-3.5 text-rose-600 ${isResetting ? 'animate-spin' : ''}`} />
              <span className="hidden md:inline">{isResetting ? 'Resetting...' : 'Reset Demo'}</span>
            </button>
          )}

          {/* Vertical Separator */}
          <div className="h-6 w-px bg-slate-200 hidden md:block" />

          {/* Zone C: Unified Enterprise User Identity & Clearance Profile Card */}
          {currentPersona && (
            <div className="relative flex items-center bg-slate-50 border border-slate-200/90 hover:border-slate-300 rounded-xl pl-2.5 pr-3 py-1.5 transition group shadow-2xs">
              {/* Initials Avatar */}
              <div className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center shrink-0 border border-indigo-200/50">
                {initials}
              </div>

              {/* User Details & Selection */}
              <div className="flex flex-col ml-2.5 text-left pr-2">
                <div className="flex items-center gap-1">
                  <span className="text-xs font-semibold text-slate-800 tracking-tight whitespace-nowrap">
                    {cleanName}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-600 transition shrink-0" />
                </div>
                <div className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono">
                  <span className="font-medium text-slate-600 truncate max-w-[110px]">{cleanRole}</span>
                  <span>•</span>
                  <span className="text-indigo-600 font-semibold">{currentPersona.clearance}</span>
                  <span>•</span>
                  <span>{currentPersona.jurisdiction} Hub</span>
                </div>
              </div>

              {/* Accessible Native Dropdown Overlay */}
              <select
                value={selectedPersonaKey}
                onChange={(e) => onSelectPersona(e.target.value)}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                title="Switch user persona & security clearance"
              >
                {Object.entries(personas).map(([key, p]) => {
                  const pClean = p.name.includes('(') ? p.name.split('(')[0].trim() : p.name;
                  return (
                    <option key={key} value={key} className="text-slate-800 bg-white">
                      {pClean} — {p.clearance} ({p.jurisdiction} Hub)
                    </option>
                  );
                })}
              </select>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
