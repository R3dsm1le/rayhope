import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Label } from 'recharts';

const AlgorithmMetricsPanel = ({ metrics }) => {
  if (!metrics) {
    return (
      <div className="p-6 bg-white rounded-lg shadow border border-gray-100 flex flex-col items-center justify-center h-full min-h-[300px]">
        <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
        <p className="text-gray-500 font-medium">Select a device to view metrics</p>
      </div>
    );
  }

  // Helper for HOW chart
  const efficiencyData = [
    { name: 'Efficiency', value: metrics.transition_efficiency },
    { name: 'Remainder', value: 100 - metrics.transition_efficiency }
  ];

  // Helper for WHEN badge
  const getPriorityColor = (priority) => {
    if (priority <= 3) return 'bg-green-100 text-green-800 border-green-200';
    if (priority <= 7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  return (
    <div className="bg-white rounded-lg shadow border border-gray-100 flex flex-col h-full">
      <div className="px-6 py-4 border-b border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800">Algorithm Analytics</h2>
        <p className="text-sm text-gray-500">Device: <span className="font-mono">{metrics.entity_id}</span></p>
      </div>
      
      <div className="p-6 flex-grow flex flex-col">
        {/* 2x2 Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          
          {/* HOW: Transition Efficiency */}
          <div className="border border-gray-100 rounded-lg p-4 flex flex-col items-center justify-center bg-gray-50/50">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">Transition Efficiency (HOW)</h3>
            <div className="w-32 h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={efficiencyData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={55}
                    startAngle={90}
                    endAngle={-270}
                    dataKey="value"
                    stroke="none"
                  >
                    <Cell key="cell-0" fill="#3b82f6" />
                    <Cell key="cell-1" fill="#e5e7eb" />
                    <Label 
                      value={`${Math.round(metrics.transition_efficiency)}`} 
                      position="center" 
                      className="text-xl font-bold fill-gray-800"
                    />
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* WHEN: Energy Priority */}
          <div className="border border-gray-100 rounded-lg p-4 flex flex-col items-center justify-center bg-gray-50/50">
            <h3 className="text-sm font-semibold text-gray-600 mb-4">Energy Priority (WHEN)</h3>
            <div className={`w-20 h-20 rounded-full flex items-center justify-center border-4 ${getPriorityColor(metrics.energy_priority).replace('bg-', 'bg-').replace('text-', 'text-').replace('border-', 'border-')}`}>
               <span className="text-3xl font-bold">{metrics.energy_priority}</span>
            </div>
            <p className="text-xs text-gray-500 mt-3 font-medium uppercase tracking-wider">Urgency Scale (1-10)</p>
          </div>

          {/* WHAT: Predictability */}
          <div className="border border-gray-100 rounded-lg p-4 flex flex-col justify-center bg-gray-50/50">
            <div className="flex justify-between items-end mb-2">
              <h3 className="text-sm font-semibold text-gray-600">Predictability (WHAT)</h3>
              <span className="text-lg font-bold text-gray-800">{metrics.predictability.toFixed(1)}%</span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-indigo-500 rounded-full transition-all duration-1000"
                style={{ width: `${metrics.predictability}%` }}
              ></div>
            </div>
          </div>

          {/* WHY: Optimization Score */}
          <div className="border border-gray-100 rounded-lg p-4 flex flex-col justify-center bg-gray-50/50">
             <div className="flex justify-between items-end mb-2">
              <h3 className="text-sm font-semibold text-gray-600">Optimization Score (WHY)</h3>
              <span className="text-lg font-bold text-gray-800">{metrics.optimization_score.toFixed(1)} <span className="text-sm font-normal text-gray-500">/ 10</span></span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-teal-500 rounded-full transition-all duration-1000"
                style={{ width: `${(metrics.optimization_score / 10) * 100}%` }}
              ></div>
            </div>
          </div>

        </div>

        {/* Bottom Additional Metrics */}
        <div className="grid grid-cols-2 gap-4 mt-auto pt-4 border-t border-gray-100">
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Total Activity</p>
            <p className="text-2xl font-bold text-gray-800">{metrics.total_activity} <span className="text-sm font-normal text-gray-500">transitions</span></p>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1">Variability (σ)</p>
            <p className="text-2xl font-bold text-gray-800">{metrics.variability.toFixed(2)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlgorithmMetricsPanel;
