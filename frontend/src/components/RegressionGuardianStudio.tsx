import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RotateCcw, 
  Plus, 
  Trash2, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ShieldCheck, 
  FlaskConical, 
  Cpu, 
  Clock, 
  Sparkles,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Terminal,
  ExternalLink
} from 'lucide-react';
import { RegressionTestCase, RegressionSuiteReport, RegressionTestResult } from '../types';

export const RegressionGuardianStudio: React.FC = () => {
  const [catalog, setCatalog] = useState<RegressionTestCase[]>([]);
  const [report, setReport] = useState<RegressionSuiteReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [runningTestId, setRunningTestId] = useState<string | null>(null);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>('ALL');
  const [expandedTestId, setExpandedTestId] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // New test form state
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('RBAC_POLP');
  const [newPersona, setNewPersona] = useState('junior_analyst');
  const [newPrompt, setNewPrompt] = useState('');
  const [newExpectedStatus, setNewExpectedStatus] = useState('DENIED_ACCESS');
  const [newKeywords, setNewKeywords] = useState('Principle of Least Privilege');
  const [newNotes, setNewNotes] = useState('');
  const [newDiscoveredBy, setNewDiscoveredBy] = useState('Human QA Tester');

  const fetchCatalog = async () => {
    try {
      const res = await fetch('/api/qa/catalog');
      const data = await res.json();
      setCatalog(data);
    } catch (e) {
      console.error('Error fetching QA catalog:', e);
    }
  };

  useEffect(() => {
    fetchCatalog();
  }, []);

  const handleRunFullSuite = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/qa/run', { method: 'POST' });
      const data: RegressionSuiteReport = await res.json();
      setReport(data);
    } catch (e) {
      console.error('Error running regression suite:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSingleTest = async (testId: string) => {
    setRunningTestId(testId);
    try {
      const res = await fetch(`/api/qa/run/${testId}`, { method: 'POST' });
      const singleResult: RegressionTestResult = await res.json();
      
      setReport(prev => {
        if (!prev) {
          return {
            total_tests: 1,
            passed_tests: singleResult.passed ? 1 : 0,
            failed_tests: singleResult.passed ? 0 : 1,
            pass_rate_percentage: singleResult.passed ? 100.0 : 0.0,
            risk_level: singleResult.passed ? 'ZERO_REGRESSION' : 'LOW_RISK',
            suite_execution_time_ms: singleResult.execution_time_ms,
            results: [singleResult],
            summary_notes: singleResult.passed ? 'Single test passed.' : 'Single test failed assertion.',
            generated_at: new Date().toLocaleTimeString()
          };
        }
        const updatedResults = prev.results.filter(r => r.test_id !== testId);
        updatedResults.push(singleResult);
        const passed = updatedResults.filter(r => r.passed).length;
        const total = updatedResults.length;
        return {
          ...prev,
          total_tests: total,
          passed_tests: passed,
          failed_tests: total - passed,
          pass_rate_percentage: Math.round((passed / total) * 100),
          results: updatedResults
        };
      });
    } catch (e) {
      console.error('Error running single test:', e);
    } finally {
      setRunningTestId(null);
    }
  };

  const handleDeleteTest = async (testId: string) => {
    if (!confirm(`Delete test scenario '${testId}'?`)) return;
    try {
      await fetch(`/api/qa/catalog/${testId}`, { method: 'DELETE' });
      await fetchCatalog();
      if (report) {
        setReport(prev => prev ? {
          ...prev,
          results: prev.results.filter(r => r.test_id !== testId)
        } : null);
      }
    } catch (e) {
      console.error('Error deleting test:', e);
    }
  };

  const handleResetBaseline = async () => {
    if (!confirm('Reset catalog to certified enterprise baseline scenarios?')) return;
    setLoading(true);
    try {
      const res = await fetch('/api/qa/reset', { method: 'POST' });
      const data = await res.json();
      setCatalog(data);
      setReport(null);
    } catch (e) {
      console.error('Error resetting catalog:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newPrompt.trim()) return;

    const testCasePayload: Partial<RegressionTestCase> = {
      title: newTitle.trim(),
      category: newCategory,
      user_persona_key: newPersona,
      prompt: newPrompt.trim(),
      expected_status: newExpectedStatus,
      expected_keywords: newKeywords ? newKeywords.split(',').map(s => s.trim()).filter(Boolean) : [],
      forbidden_keywords: [],
      discovered_by: newDiscoveredBy.trim() || 'Human QA Tester',
      discovery_notes: newNotes.trim()
    };

    try {
      await fetch('/api/qa/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testCasePayload)
      });
      await fetchCatalog();
      setIsAddModalOpen(false);
      // Reset form
      setNewTitle('');
      setNewPrompt('');
      setNewNotes('');
    } catch (err) {
      console.error('Error saving custom test case:', err);
    }
  };

  const categories = [
    { key: 'ALL', label: 'All Scenarios' },
    { key: 'RBAC_POLP', label: 'RBAC / PoLP' },
    { key: 'CIRCUIT_BREAKER', label: 'Circuit Breaker' },
    { key: 'PROMPT_INJECTION', label: 'Prompt Ingress' },
    { key: 'PII_PRIVACY', label: 'PII Privacy Vault' },
    { key: 'FIDUCIARY_SUITABILITY', label: 'Fiduciary Advice' },
    { key: 'GOLD_GROUNDING', label: 'Gold Grounding' }
  ];

  const filteredCatalog = catalog.filter(t => 
    activeCategoryFilter === 'ALL' || t.category === activeCategoryFilter
  );

  const getResultForTest = (testId: string): RegressionTestResult | undefined => {
    return report?.results.find(r => r.test_id === testId);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Fail-Safe Architecture Intro */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5 mb-1.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
                <FlaskConical className="w-4 h-4" />
              </div>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">
                Regression Guardian & HITL QA Testing Studio
              </h2>
              <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                Agent 4: Continuous Verification
              </span>
            </div>
            <p className="text-xs text-slate-500 max-w-3xl leading-relaxed">
              Acts as an automated fail-safe mechanism during rapid vibe-coding iterations. Whenever you discover an anomaly or testing bug, the Guardian retains the exact human-in-the-loop context (persona, prompt, assertion criteria, and notes), cataloging it for one-click re-testing on every application update.
            </p>
          </div>

          <div className="flex items-center space-x-2.5 shrink-0">
            <button
              onClick={() => setIsAddModalOpen(true)}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition shadow-sm"
            >
              <Plus className="w-3.5 h-3.5 text-indigo-600" />
              <span>Record Anomaly</span>
            </button>
            <button
              onClick={handleResetBaseline}
              disabled={loading}
              className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition shadow-sm disabled:opacity-50"
              title="Restore original enterprise baseline tests"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>Reset Baseline</span>
            </button>
            <button
              onClick={handleRunFullSuite}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-700 transition shadow-sm disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Play className="w-3.5 h-3.5 fill-current" />
              )}
              <span>Run Full Regression Suite</span>
            </button>
          </div>
        </div>

        {/* Executive Scorecard */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-5 border-t border-slate-100">
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
              Cataloged Scenarios
            </span>
            <span className="text-xl font-bold text-slate-900">{catalog.length} Tests</span>
          </div>

          <div className="p-3.5 rounded-xl bg-emerald-50/50 border border-emerald-200/80">
            <span className="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider block mb-1">
              Passing Assertions
            </span>
            <div className="flex items-baseline space-x-1.5">
              <span className="text-xl font-bold text-emerald-900">
                {report ? report.passed_tests : '—'}
              </span>
              {report && (
                <span className="text-xs font-bold text-emerald-700">
                  ({report.pass_rate_percentage}%)
                </span>
              )}
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-rose-50/50 border border-rose-200/80">
            <span className="text-[11px] font-semibold text-rose-700 uppercase tracking-wider block mb-1">
              Regressions Detected
            </span>
            <span className="text-xl font-bold text-rose-900">
              {report ? report.failed_tests : '—'}
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-indigo-50/50 border border-indigo-200/80">
            <span className="text-[11px] font-semibold text-indigo-700 uppercase tracking-wider block mb-1">
              Regression Risk Level
            </span>
            <span className="text-sm font-bold text-indigo-900 flex items-center space-x-1 mt-1">
              {report ? (
                <>
                  <ShieldCheck className="w-4 h-4 text-emerald-600 inline mr-1" />
                  <span>{report.risk_level.replace('_', ' ')}</span>
                </>
              ) : (
                <span className="text-slate-500 font-normal">Suite Awaiting Execution</span>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Category Filter Navigation */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {categories.map(cat => (
          <button
            key={cat.key}
            onClick={() => setActiveCategoryFilter(cat.key)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition ${
              activeCategoryFilter === cat.key
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Test Scenarios Matrix */}
      <div className="space-y-3">
        {filteredCatalog.map(test => {
          const res = getResultForTest(test.test_id);
          const isExpanded = expandedTestId === test.test_id;
          const isRunningThis = runningTestId === test.test_id;

          return (
            <div
              key={test.test_id}
              className={`bg-white border rounded-2xl transition shadow-sm overflow-hidden ${
                res 
                  ? res.passed 
                    ? 'border-emerald-200' 
                    : 'border-rose-300 ring-1 ring-rose-200' 
                  : 'border-slate-200'
              }`}
            >
              {/* Main Test Row */}
              <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-start space-x-3 flex-1 min-w-0">
                  <div className="mt-0.5 shrink-0">
                    {res ? (
                      res.passed ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                      ) : (
                        <XCircle className="w-5 h-5 text-rose-600" />
                      )
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-slate-300 border-dashed"></div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="text-xs font-mono font-bold text-slate-500">
                        {test.test_id}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900 truncate">
                        {test.title}
                      </h4>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
                        {test.category}
                      </span>
                      {test.is_baseline && (
                        <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-amber-50 text-amber-700 border border-amber-200">
                          CERTIFIED BASELINE
                        </span>
                      )}
                    </div>

                    <div className="text-[11px] text-slate-600 font-mono line-clamp-1">
                      Target: <strong className="text-indigo-700 font-semibold">{test.user_persona_key}</strong> | Prompt: "{test.prompt}"
                    </div>
                  </div>
                </div>

                {/* Right Result & Action Controls */}
                <div className="flex items-center space-x-3 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
                  {/* Expected vs Actual Pill */}
                  <div className="flex flex-col text-right">
                    <span className="text-[10px] uppercase font-mono text-slate-500">
                      Expected: <strong className="text-slate-800">{test.expected_status}</strong>
                    </span>
                    {res && (
                      <span className={`text-[10px] uppercase font-mono font-bold ${
                        res.passed ? 'text-emerald-700' : 'text-rose-700'
                      }`}>
                        Actual: {res.actual_status} ({res.execution_time_ms}ms)
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-1.5">
                    <button
                      onClick={() => handleRunSingleTest(test.test_id)}
                      disabled={isRunningThis || loading}
                      className="p-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition disabled:opacity-50"
                      title="Run this scenario"
                    >
                      {isRunningThis ? (
                        <div className="w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                      ) : (
                        <Play className="w-3.5 h-3.5" />
                      )}
                    </button>

                    <button
                      onClick={() => setExpandedTestId(isExpanded ? null : test.test_id)}
                      className="p-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 hover:bg-slate-100 transition"
                      title="Toggle inspection details"
                    >
                      {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {!test.is_baseline && (
                      <button
                        onClick={() => handleDeleteTest(test.test_id)}
                        className="p-1.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-400 hover:text-rose-600 transition"
                        title="Delete custom test"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Expandable Verification Details */}
              {isExpanded && (
                <div className="px-5 py-4 bg-slate-50/70 border-t border-slate-200 text-xs space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="bg-white p-3 rounded-xl border border-slate-200 space-y-1">
                      <span className="text-[10px] font-bold uppercase text-slate-500 block">
                        Human Tester Notes & Discovery Context
                      </span>
                      <p className="text-slate-700 italic">
                        {test.discovery_notes || 'Captured by human in the loop during interactive vibe testing.'}
                      </p>
                      <span className="text-[10px] text-slate-500 block mt-1">
                        Discovered by: <strong>{test.discovered_by}</strong> ({test.created_at})
                      </span>
                    </div>

                    <div className="bg-white p-3 rounded-xl border border-slate-200 space-y-1">
                      <span className="text-[10px] font-bold uppercase text-slate-500 block">
                        Assertion Criteria
                      </span>
                      <div className="space-y-0.5 text-slate-700">
                        <div>Expected Status: <strong className="text-indigo-700">{test.expected_status}</strong></div>
                        <div>Required Keywords: <code className="bg-slate-100 px-1 py-0.5 rounded text-[11px]">{test.expected_keywords.join(', ') || 'None'}</code></div>
                      </div>
                    </div>
                  </div>

                  {res && (
                    <div className={`p-3.5 rounded-xl border ${
                      res.passed 
                        ? 'bg-emerald-50/60 border-emerald-200 text-emerald-950' 
                        : 'bg-rose-50/70 border-rose-200 text-rose-950'
                    }`}>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold uppercase tracking-wider text-[10px]">
                          Live Agent Execution Trace
                        </span>
                        <span className="font-mono text-[10px]">
                          Duration: {res.execution_time_ms} ms
                        </span>
                      </div>
                      <p className="font-mono text-[11px] bg-white/70 p-2.5 rounded-lg border border-slate-200/50 mb-2">
                        {res.actual_reply_snippet}
                      </p>
                      {res.diagnostic_hint && (
                        <div className="mt-2 p-2.5 rounded-lg bg-rose-100/70 border border-rose-300 text-rose-900 text-xs">
                          <strong>Automated Diagnostic Hint:</strong> {res.diagnostic_hint}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Add Custom Test Case Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-xl w-full p-6 animate-fadeIn">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <FlaskConical className="w-5 h-5 text-indigo-600" />
                <h3 className="text-sm font-bold text-slate-900">
                  Record Anomaly into Regression Guardian Vault
                </h3>
              </div>
              <button
                onClick={() => setIsAddModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 font-bold text-lg"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleCreateTest} className="space-y-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Scenario Title</label>
                <input
                  type="text"
                  placeholder="e.g. Rachel Lim Commercial Lease PoLP Bypass"
                  value={newTitle}
                  onChange={e => setNewTitle(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Target Persona</label>
                  <select
                    value={newPersona}
                    onChange={e => setNewPersona(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    <option value="junior_analyst">Rachel Lim (Junior Analyst)</option>
                    <option value="wealth_advisor">Vikram Mehta (Senior Wealth Advisor)</option>
                    <option value="compliance_officer">Priya Sharma (Compliance Auditor)</option>
                    <option value="risk_officer">Marcus Vance (Chief Risk Officer)</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={e => setNewCategory(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    <option value="RBAC_POLP">RBAC / Least Privilege (PoLP)</option>
                    <option value="CIRCUIT_BREAKER">Circuit Breaker & Four-Eyes</option>
                    <option value="PROMPT_INJECTION">Prompt Ingress & Jailbreak</option>
                    <option value="PII_PRIVACY">PII Vault / Privacy</option>
                    <option value="FIDUCIARY_SUITABILITY">Fiduciary Suitability</option>
                    <option value="GOLD_GROUNDING">Gold Grounding & Accuracy</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Verbatim Testing Prompt</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Please execute commercial lease deposit of S$ 75,000..."
                  value={newPrompt}
                  onChange={e => setNewPrompt(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 block mb-1">Expected Status</label>
                  <select
                    value={newExpectedStatus}
                    onChange={e => setNewExpectedStatus(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                  >
                    <option value="DENIED_ACCESS">DENIED_ACCESS</option>
                    <option value="PENDING_HITL_APPROVAL">PENDING_HITL_APPROVAL</option>
                    <option value="BLOCKED_ATTACK">BLOCKED_ATTACK</option>
                    <option value="COMPLETED">COMPLETED</option>
                  </select>
                </div>

                <div>
                  <label className="font-bold text-slate-700 block mb-1">Required Keywords (comma-separated)</label>
                  <input
                    type="text"
                    placeholder="e.g. Principle of Least Privilege"
                    value={newKeywords}
                    onChange={e => setNewKeywords(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 block mb-1">Human Tester Discovery Notes</label>
                <textarea
                  rows={2}
                  placeholder="What anomaly did you observe during manual testing? What is the expected behavior?"
                  value={newNotes}
                  onChange={e => setNewNotes(e.target.value)}
                  className="w-full p-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition"
                >
                  Save to Test Vault
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
