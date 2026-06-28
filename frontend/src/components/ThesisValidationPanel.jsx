import React, { useState } from 'react';

const API_BASE = 'http://localhost:8000/api/validation';

// --- Helper sub-components ---

const InterpretationBadge = ({ text }) => {
  if (!text) return null;
  const positive = ['Stable', 'Robust', 'Excellent', 'Good', 'Valid', 'All tests passed', 'validates'];
  const moderate = ['Moderate', 'Sensitive'];
  const isPositive = positive.some(w => text.includes(w));
  const isModerate = moderate.some(w => text.includes(w));

  const cls = isPositive
    ? 'bg-green-100 text-green-800 border border-green-300'
    : isModerate
    ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
    : 'bg-red-100 text-red-800 border border-red-300';

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-bold ${cls}`}>
      {isPositive ? '✓' : isModerate ? '⚠' : '✗'}&nbsp;{text}
    </span>
  );
};

const SmallTable = ({ rows }) => (
  <table className="w-full text-xs mt-3 border border-gray-200 rounded overflow-hidden">
    <tbody>
      {rows.map(([label, value], i) => (
        <tr key={i} className={i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
          <td className="px-3 py-1.5 font-medium text-gray-600 w-1/2">{label}</td>
          <td className="px-3 py-1.5 text-gray-800 font-mono">{String(value)}</td>
        </tr>
      ))}
    </tbody>
  </table>
);

// Rich elbow analysis card showing all three signals + majority vote
const ElbowAnalysisDetail = ({ result }) => {
  if (!result) return null;

  const signals = [
    {
      id: 'signal_percentage',
      label: 'Signal 1 — % Reduction',
      description: 'First k where inertia drop falls below 15% of total range reduction.',
      value: result.signal_percentage,
    },
    {
      id: 'signal_second_derivative',
      label: 'Signal 2 — 2nd Derivative',
      description: 'k at maximum curvature (sharpest bend) of the inertia curve.',
      value: result.signal_second_derivative,
    },
    {
      id: 'signal_kneedle',
      label: 'Signal 3 — Kneedle',
      description: 'k at maximum perpendicular distance from chord (Satopaa et al., 2011).',
      value: result.signal_kneedle,
    },
  ];

  const identified = result.identified_elbow;
  const confirmsK3 = result.confirms_k3;

  // Count how many signals agree with the majority vote result
  const agreeCount = signals.filter(s => s.value === identified).length;

  return (
    <div className="mt-3 space-y-3">
      {/* Three signal cards */}
      <div className="grid grid-cols-3 gap-2">
        {signals.map(sig => {
          const agrees = sig.value === identified;
          return (
            <div
              key={sig.id}
              className={`rounded-lg p-3 border text-center ${
                agrees
                  ? 'bg-violet-50 border-violet-300'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <p className="text-xs font-semibold text-gray-500 mb-1 leading-tight">{sig.label}</p>
              <p className={`text-2xl font-bold mb-1 ${agrees ? 'text-violet-700' : 'text-gray-500'}`}>
                k={sig.value}
              </p>
              <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${
                agrees ? 'bg-violet-200 text-violet-800' : 'bg-gray-200 text-gray-600'
              }`}>
                {agrees ? '✓ agrees' : '✗ diverges'}
              </span>
              <p className="text-xs text-gray-400 mt-1.5 leading-tight">{sig.description}</p>
            </div>
          );
        })}
      </div>

      {/* Majority vote result */}
      <div className={`rounded-lg p-4 border flex items-center justify-between gap-4 ${
        confirmsK3 ? 'bg-green-50 border-green-300' : 'bg-yellow-50 border-yellow-300'
      }`}>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-0.5">
            Majority Vote — {agreeCount === 3 ? 'unanimous' : agreeCount === 2 ? '2 of 3 agree' : 'all disagree, using median'}
          </p>
          <p className={`text-xl font-bold ${confirmsK3 ? 'text-green-800' : 'text-yellow-800'}`}>
            Identified elbow: k={identified}
          </p>
        </div>
        <span className={`text-sm font-bold px-3 py-1.5 rounded-full ${
          confirmsK3 ? 'bg-green-200 text-green-900' : 'bg-yellow-200 text-yellow-900'
        }`}>
          {confirmsK3 ? '✓ Confirms k=3' : `✗ k=${identified} ≠ 3`}
        </span>
      </div>

      {/* Inertia table */}
      <div>
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Inertia by k</p>
        <table className="w-full text-xs border border-gray-200 rounded overflow-hidden">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th className="px-3 py-1.5 text-left font-medium">k</th>
              <th className="px-3 py-1.5 text-left font-medium">Inertia</th>
              <th className="px-3 py-1.5 text-left font-medium">Marginal reduction</th>
            </tr>
          </thead>
          <tbody>
            {(result.elbow_results || []).map((r, i) => {
              const isElbow = r.k === identified;
              return (
                <tr
                  key={r.k}
                  className={`${isElbow ? 'bg-violet-50 font-bold' : i % 2 === 0 ? 'bg-white' : 'bg-gray-50'} border-t border-gray-100`}
                >
                  <td className={`px-3 py-1.5 font-mono ${isElbow ? 'text-violet-700' : 'text-gray-700'}`}>
                    {isElbow ? `★ k=${r.k}` : `k=${r.k}`}
                  </td>
                  <td className={`px-3 py-1.5 font-mono ${isElbow ? 'text-violet-700' : 'text-gray-800'}`}>
                    {r.inertia?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className={`px-3 py-1.5 font-mono ${isElbow ? 'text-violet-700' : 'text-gray-500'}`}>
                    {r.marginal_reduction_percent != null ? `${r.marginal_reduction_percent}%` : '—'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const TestResultView = ({ name, result }) => {
  if (!result) return null;

  const interp = result.interpretation || result.summary?.overall_status || '';

  let rows = [];
  if (name === 'feature-validity') {
    rows = [
      ['All in range', String(result.all_in_range)],
      ['No degenerate columns', String(result.no_degenerate_columns)],
    ];
    if (result.feature_stats) {
      Object.entries(result.feature_stats).forEach(([col, stats]) => {
        rows.push([`${col} mean`, stats.mean?.toFixed(3)]);
        rows.push([`${col} std`, stats.std?.toFixed(3)]);
      });
    }
  } else if (name === 'cluster-consistency') {
    rows = [
      ['Consistency Rate', `${result.consistency_rate?.toFixed(2)}%`],
      ['Seeds Used', result.seeds_used?.join(', ')],
    ];
    (result.runs || []).forEach((r, i) => {
      rows.push([`Seed ${r.seed} Silhouette`, r.silhouette_score?.toFixed(4)]);
    });
  } else if (name === 'elbow-analysis') {
    // Elbow analysis gets a custom rich render — return empty rows and let the
    // ElbowAnalysisDetail component below handle the display.
    rows = [];
  } else if (name === 'noise-tolerance') {
    const sigmaLabels = {
      0.05:  'API jitter',
      0.1:   'sensor drift',
      0.2:   'heavy degradation ← threshold',
      0.3:   'adversarial floor',
    };
    rows = [['Baseline Silhouette', result.baseline_silhouette?.toFixed(4)]];
    (result.noise_results || []).forEach(r => {
      const label = sigmaLabels[r.sigma] ? `σ=${r.sigma} (${sigmaLabels[r.sigma]})` : `σ=${r.sigma}`;
      rows.push([label, r.silhouette_score?.toFixed(4)]);
    });
  } else if (name === 'ground-truth-accuracy') {
    rows = [
      ['Overall Accuracy', `${result.overall_accuracy?.toFixed(2)}%`],
      ['Matched Observations', result.total_matched],
      ['Unmatched', result.total_unmatched],
    ];
    if (result.per_profile_accuracy) {
      Object.entries(result.per_profile_accuracy).forEach(([p, acc]) => {
        rows.push([p, `${acc?.toFixed(2)}%`]);
      });
    }
  }

  return (
    <div className="mt-3">
      <InterpretationBadge text={interp} />
      {name === 'elbow-analysis' ? (
        <ElbowAnalysisDetail result={result} />
      ) : rows.length > 0 ? (
        <SmallTable rows={rows} />
      ) : null}
    </div>
  );
};

// --- Individual test card ---

const TEST_CONFIG = [
  {
    id: 'feature-validity',
    title: 'Feature Vector Validity',
    description: 'Confirms all six algorithm outputs are within valid ranges and non-degenerate.',
    endpoint: '/feature-validity',
    method: 'GET',
  },
  {
    id: 'cluster-consistency',
    title: 'Cluster Consistency',
    description: 'Measures assignment stability across five independent K-Means runs with different seeds.',
    endpoint: '/cluster-consistency',
    method: 'GET',
  },
  {
    id: 'elbow-analysis',
    title: 'Elbow Analysis',
    description: 'Confirms k=3 is the statistically optimal cluster count using inertia reduction.',
    endpoint: '/elbow-analysis',
    method: 'GET',
  },
  {
    id: 'noise-tolerance',
    title: 'Noise Tolerance',
    description: 'Tests model robustness against realistic IoT noise levels calibrated to Home Assistant API data (σ=0.05–0.3). The API smooths raw sensor readings before exposure, so the robustness threshold is evaluated at σ=0.2 (heavy degradation) rather than the unrealistically severe σ=0.5 used for raw sensor streams.',
    endpoint: '/noise-tolerance',
    method: 'GET',
  },
  {
    id: 'ground-truth-accuracy',
    title: 'Ground Truth Accuracy',
    description: 'Compares K-Means predicted profiles to synthetic generator ground truth labels.',
    endpoint: '/ground-truth-accuracy',
    method: 'GET',
  },
];

const TestCard = ({ config }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}${config.endpoint}`, { method: config.method });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-5 flex flex-col">
      <h3 className="font-bold text-gray-800 text-sm mb-1">{config.title}</h3>
      <p className="text-xs text-gray-500 mb-4 flex-grow">{config.description}</p>

      <button
        onClick={run}
        disabled={loading}
        className="self-start px-4 py-1.5 text-xs font-semibold rounded bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 transition"
      >
        {loading ? 'Running…' : 'Run Test'}
      </button>

      {loading && (
        <div className="flex items-center gap-2 mt-3 text-xs text-gray-500">
          <div className="animate-spin w-3 h-3 border-2 border-violet-400 border-t-transparent rounded-full"></div>
          Computing…
        </div>
      )}

      {error && <p className="mt-3 text-xs text-red-600">{error}</p>}

      {result && <TestResultView name={config.id} result={result} />}
    </div>
  );
};

// --- Full suite runner section ---

const FullSuiteRunner = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [openSections, setOpenSections] = useState({});

  const run = async () => {
    setLoading(true);
    setResults(null);
    try {
      const res = await fetch(`${API_BASE}/run-full-suite`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResults(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (key) => setOpenSections(prev => ({ ...prev, [key]: !prev[key] }));

  const summaryTestNames = {
    feature_vector_validity: 'Feature Vector Validity',
    cluster_consistency: 'Cluster Consistency',
    elbow_analysis: 'Elbow Analysis',
    noise_tolerance: 'Noise Tolerance',
    ground_truth_accuracy: 'Ground Truth Accuracy',
  };

  // Map result key to test card id (for TestResultView to work correctly)
  const keyToCardId = {
    feature_vector_validity: 'feature-validity',
    cluster_consistency: 'cluster-consistency',
    elbow_analysis: 'elbow-analysis',
    noise_tolerance: 'noise-tolerance',
    ground_truth_accuracy: 'ground-truth-accuracy',
  };

  return (
    <div className="mt-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-bold text-gray-800">Full Validation Suite</h2>
          <p className="text-sm text-gray-500">Runs all five tests sequentially and returns the complete thesis validation report.</p>
        </div>
        <button
          onClick={run}
          disabled={loading}
          className="px-6 py-2.5 bg-violet-600 text-white font-bold rounded-lg hover:bg-violet-700 disabled:opacity-50 transition shadow"
        >
          {loading ? 'Running all tests…' : '▶ Run Full Validation Suite'}
        </button>
      </div>

      {loading && (
        <div className="flex items-center justify-center gap-3 bg-violet-50 border border-violet-200 rounded-lg p-8">
          <div className="animate-spin w-6 h-6 border-4 border-violet-500 border-t-transparent rounded-full"></div>
          <span className="text-violet-700 font-medium">Running all 5 validation tests — this may take 30–60 seconds…</span>
        </div>
      )}

      {results && (
        <div className="space-y-6">
          {/* Overall status banner */}
          {results.summary && (
            <div className={`rounded-lg p-5 border ${results.summary.overall_status === 'All tests passed' ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1">Suite Result</p>
                  <InterpretationBadge text={results.summary.overall_status} />
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Completed</p>
                  <p className="text-sm font-mono text-gray-700">{new Date(results.summary.timestamp).toLocaleString()}</p>
                  <p className="text-xs text-gray-500">{results.summary.total_duration_seconds}s total</p>
                </div>
              </div>
            </div>
          )}

          {/* Summary table */}
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-5 py-3 bg-gray-50 border-b border-gray-200">
              <h3 className="font-bold text-gray-700 text-sm">Committee Summary View</h3>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-xs uppercase text-gray-500 border-b border-gray-200">
                  <th className="px-5 py-3 text-left font-medium">Test</th>
                  <th className="px-5 py-3 text-left font-medium">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {Object.entries(summaryTestNames).map(([key, label]) => {
                  const r = results[key];
                  const interp = r?.interpretation || '—';
                  return (
                    <tr key={key}>
                      <td className="px-5 py-3 font-medium text-gray-800">{label}</td>
                      <td className="px-5 py-3"><InterpretationBadge text={interp} /></td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Collapsible detailed results */}
          {Object.entries(summaryTestNames).map(([key, label]) => {
            const r = results[key];
            const isOpen = openSections[key];
            return (
              <div key={key} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                <button
                  onClick={() => toggleSection(key)}
                  className="w-full flex items-center justify-between px-5 py-4 hover:bg-gray-50 transition text-left"
                >
                  <span className="font-semibold text-gray-800 text-sm">{label}</span>
                  <span className="text-gray-400 text-lg">{isOpen ? '▲' : '▼'}</span>
                </button>
                {isOpen && r && (
                  <div className="px-5 pb-5 border-t border-gray-100">
                    <TestResultView name={keyToCardId[key]} result={r} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// --- Main tab component ---

const ThesisValidationPanel = () => {
  return (
    <div>
      {/* Academic validation banner */}
      <div className="mb-8 rounded-lg bg-violet-700 px-6 py-4 flex items-center gap-4 shadow">
        <svg className="w-7 h-7 text-violet-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
        </svg>
        <div>
          <p className="font-bold text-white text-lg">Academic Validation — Phase 2</p>
          <p className="text-violet-200 text-sm">
            All tests are read-only and isolated from the production pipeline. Results constitute thesis evidence.
          </p>
        </div>
      </div>

      {/* Individual test cards */}
      <h2 className="text-lg font-bold text-gray-800 mb-4">Individual Validation Tests</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {TEST_CONFIG.map(config => (
          <TestCard key={config.id} config={config} />
        ))}
      </div>

      {/* Full suite */}
      <FullSuiteRunner />
    </div>
  );
};

export default ThesisValidationPanel;
