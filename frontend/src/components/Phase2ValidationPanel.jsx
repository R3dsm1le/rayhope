import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Phase2ValidationPanel = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runClustering = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/phase2/cluster', {
        method: 'POST'
      });
      if (!response.ok) {
        throw new Error('Failed to run clustering pipeline.');
      }
      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      setError('Error running Phase 2 validation. Did you run the generation pipeline first?');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-white rounded-lg shadow border border-gray-100 p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
        <p className="text-gray-600">Running K-Means Clustering on 1,500 records...</p>
      </div>
    );
  }

  if (!results && !error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-white rounded-lg shadow border border-gray-100 p-8">
        <svg className="w-16 h-16 text-indigo-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
        <p className="text-gray-500 mb-6">Run the clustering pipeline to see Phase 2 validation results</p>
        <button 
          onClick={runClustering}
          className="px-6 py-2 bg-indigo-600 text-white rounded-md shadow-sm hover:bg-indigo-700 transition font-medium"
        >
          Run K-Means Clustering
        </button>
      </div>
    );
  }

  // Formatting for Recharts
  const chartData = results ? Object.entries(results.cluster_counts).map(([name, count]) => ({ name, count })) : [];
  
  // Custom colors for bars
  const colors = {
    'Water Guardians': '#3b82f6', // blue
    'Conscious Users': '#10b981', // green
    'Green Opportunity': '#f59e0b' // yellow
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {results && (
        <>
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">Validation Metrics</h2>
            <button 
              onClick={runClustering}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition text-sm font-medium border border-gray-300"
            >
              Rerun Clustering
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Silhouette Score */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-100 flex flex-col justify-center">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Silhouette Coefficient</h3>
              <div className="flex items-end gap-3 mb-2">
                <span className="text-4xl font-bold text-gray-800">{results.silhouette_coefficient.toFixed(3)}</span>
                {results.silhouette_coefficient > 0.7 ? (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">STRONG</span>
                ) : results.silhouette_coefficient > 0.5 ? (
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded">GOOD</span>
                ) : (
                  <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-bold rounded">WEAK</span>
                )}
              </div>
              <p className="text-xs text-gray-500">Measures cluster cohesion. Target is &gt; 0.5.</p>
            </div>

            {/* Davies-Bouldin Score */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-100 flex flex-col justify-center">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Davies-Bouldin Index</h3>
              <div className="flex items-end gap-3 mb-2">
                <span className="text-4xl font-bold text-gray-800">{results.davies_bouldin_index.toFixed(3)}</span>
                {results.davies_bouldin_index < 1.0 ? (
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">GOOD</span>
                ) : (
                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded">HIGH</span>
                )}
              </div>
              <p className="text-xs text-gray-500">Measures cluster separation. Target is &lt; 1.0.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Cluster Counts Chart */}
            <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
              <h3 className="text-md font-semibold text-gray-800 mb-6">Observations per Cluster</h3>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                    <XAxis dataKey="name" tick={{fontSize: 12}} />
                    <YAxis />
                    <Tooltip cursor={{fill: '#f3f4f6'}} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={colors[entry.name] || '#8884d8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Tables */}
            <div className="space-y-6 flex flex-col">
              {/* Dynamic Label Map */}
              <div className="bg-white rounded-lg shadow border border-gray-100 overflow-hidden flex-grow">
                <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
                  <h3 className="text-sm font-semibold text-gray-800">Dynamic Label Assignment</h3>
                </div>
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-gray-500 bg-gray-50">
                    <tr>
                      <th className="px-4 py-2">K-Means Index</th>
                      <th className="px-4 py-2">Assigned Profile</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {Object.entries(results.cluster_label_map).map(([index, label]) => (
                      <tr key={index}>
                        <td className="px-4 py-3 font-mono font-medium text-gray-600">{index}</td>
                        <td className="px-4 py-3 font-medium text-gray-800">
                          <span className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full" style={{backgroundColor: colors[label] || '#000'}}></span>
                            {label}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Elbow Analysis */}
              <div className="bg-white rounded-lg shadow border border-gray-100 overflow-hidden">
                <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
                  <h3 className="text-sm font-semibold text-gray-800">Elbow Analysis</h3>
                </div>
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-gray-500 bg-gray-50">
                    <tr>
                      <th className="px-4 py-2">k (Clusters)</th>
                      <th className="px-4 py-2">Inertia</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {Object.entries(results.elbow_analysis).map(([k, inertia]) => (
                      <tr key={k} className={k === '3' ? 'bg-indigo-50/50' : ''}>
                        <td className={`px-4 py-2 font-mono ${k === '3' ? 'font-bold text-indigo-700' : 'text-gray-600'}`}>{k}</td>
                        <td className={`px-4 py-2 ${k === '3' ? 'font-bold text-indigo-700' : 'text-gray-800'}`}>{Number(inertia).toLocaleString(undefined, {maximumFractionDigits: 0})}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Phase2ValidationPanel;
