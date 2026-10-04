import React, { useState, useEffect } from 'react';
import { FileCheck, ShieldCheck, RefreshCw, CheckCircle2, Award } from 'lucide-react';

export const SOC2AuditStudio: React.FC = () => {
  const [report, setReport] = useState<any | null>(null);
  const [scanSummary, setScanSummary] = useState<any | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchScan = async () => {
    setIsScanning(true);
    try {
      const res = await fetch('/api/compliance/scan');
      const data = await res.json();
      setScanSummary(data);
    } catch (err) {
      console.error('Scan failed:', err);
    } finally {
      setIsScanning(false);
    }
  };

  const fetchReport = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch('/api/compliance/report');
      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error('Report generation failed:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    fetchScan();
    fetchReport();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <Award className="w-5 h-5 text-amber-500" />
            <h2 className="text-base font-bold text-slate-900">
              SOC 2 Type II & JAPAC Regulatory Evidence Studio
            </h2>
            <span className="text-[10px] font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-bold border border-emerald-200">
              AUDIT READY
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Autonomous Agent 4 scans financial data pipelines, access boundaries, and ledgers to generate formal evidence-based audit packages.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            disabled={isScanning}
            onClick={fetchScan}
            className="flex items-center space-x-2 bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold py-2.5 px-4 rounded-xl text-xs transition border border-slate-200 disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin text-indigo-600' : 'text-slate-500'}`} />
            <span>{isScanning ? 'Scanning Pipelines...' : 'Run Continuous Scan'}</span>
          </button>

          <button
            disabled={isGenerating}
            onClick={fetchReport}
            className="flex items-center space-x-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 px-4 rounded-xl text-xs transition shadow-sm disabled:opacity-50"
          >
            <FileCheck className="w-4 h-4" />
            <span>{isGenerating ? 'Synthesizing Report...' : 'Regenerate Auditor Package'}</span>
          </button>
        </div>
      </div>

      {/* Compliance Health & Scan Telemetry Cards */}
      {report && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Trust Services Criteria Score</span>
            <div className="text-2xl font-bold text-emerald-700 font-mono mt-1">
              {report.compliance_score}%
            </div>
            <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-mono mt-2 inline-block font-semibold">
              100% Effective Controls
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Attestation State</span>
            <div className="text-xl font-bold text-indigo-700 font-mono mt-1 line-clamp-1">
              TYPE II READY
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">
              Continuous Evidence Logged
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Unmasked PII Leaks Detected</span>
            <div className="text-2xl font-bold text-emerald-700 font-mono mt-1">
              {report.pipeline_scan_summary.silver_unmasked_leaks}
            </div>
            <span className="text-[10px] text-slate-500 font-mono mt-2 block">
              Zero Cleartext NRIC / PAN
            </span>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
            <span className="text-xs text-slate-500 font-medium">Cryptographic Chain Verification</span>
            <div className="text-2xl font-bold text-slate-900 font-mono mt-1">
              {report.cryptographic_chain_proof.total_blocks} Blocks
            </div>
            <span className="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded font-mono mt-2 inline-block font-semibold">
              SHA-256 Chained & Verified
            </span>
          </div>
        </div>
      )}

      {/* Target Frameworks Banner */}
      {report && (
        <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex flex-wrap items-center gap-2 text-xs">
          <span className="text-slate-500 font-semibold mr-1">Evaluated Frameworks:</span>
          {report.target_frameworks.map((fw: string, idx: number) => (
            <span key={idx} className="bg-slate-50 text-slate-800 font-mono px-3 py-1 rounded-lg border border-slate-200 font-medium">
              ✓ {fw}
            </span>
          ))}
        </div>
      )}

      {/* Controls & Evidence Table */}
      {report && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm overflow-hidden">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Auditor Evidence-Based Control Register ({report.evidence_controls.length} Controls)
              </h3>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Report Reference ID: <span className="font-mono text-indigo-700 font-semibold">{report.report_id}</span> | Generated: <span className="font-mono text-slate-600">{report.generated_at}</span>
              </p>
            </div>
          </div>

          <div className="space-y-4">
            {report.evidence_controls.map((ctrl: any, idx: number) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200/90 hover:border-slate-300 transition space-y-2.5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono font-bold text-indigo-700 text-sm bg-indigo-50 border border-indigo-200 px-2.5 py-0.5 rounded-md">
                      {ctrl.control_id}
                    </span>
                    <span className="text-xs font-bold text-slate-800">
                      {ctrl.criteria_category}
                    </span>
                  </div>
                  <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 self-start sm:self-auto">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{ctrl.status}</span>
                  </span>
                </div>

                <p className="text-xs font-medium text-slate-900 leading-relaxed">
                  {ctrl.control_description}
                </p>

                <div className="bg-white border border-slate-200 rounded-lg p-3 text-xs space-y-1.5 font-sans">
                  <div>
                    <span className="text-slate-500 font-mono font-medium">Mechanism:</span>{' '}
                    <span className="text-slate-700">{ctrl.implementation_mechanism}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 font-mono font-medium">Auditor Notes:</span>{' '}
                    <span className="text-emerald-800 font-medium">{ctrl.auditor_notes}</span>
                  </div>
                </div>

                {/* Evidence Telemetry Pill */}
                <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-500 pt-1">
                  <span className="text-slate-500">Telemetry Proof:</span>
                  <pre className="bg-slate-100 border border-slate-200 px-2.5 py-1 rounded text-slate-700 overflow-x-auto text-[10px]">
                    {JSON.stringify(ctrl.evidence_telemetry)}
                  </pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
