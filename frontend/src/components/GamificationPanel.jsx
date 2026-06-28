import React, { useState, useEffect } from 'react';

const GamificationPanel = ({ selectedDevice, gamificationData }) => {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    // Fetch leaderboard
    const fetchLeaderboard = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/leaderboard');
        if (response.ok) {
          const data = await response.json();
          setLeaderboard(data);
        }
      } catch (e) {
        console.error("Failed to fetch leaderboard", e);
      }
    };
    
    fetchLeaderboard();
    
    // Poll every 60s
    const id = setInterval(fetchLeaderboard, 60000);
    return () => clearInterval(id);
  }, []);

  if (!gamificationData) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
      
      {/* Savings Tracker */}
      <div className="lg:col-span-1 bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg shadow border border-green-200 p-6 flex flex-col justify-center">
        <h3 className="text-sm font-semibold text-green-800 uppercase tracking-wider mb-6 flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          Savings Tracker
        </h3>
        
        <div className="space-y-6">
          <div>
            <p className="text-xs text-green-700 font-medium uppercase mb-1">Energy Saved</p>
            <p className="text-3xl font-bold text-green-900">{gamificationData.savings_kwh.toFixed(4)} <span className="text-sm font-medium text-green-700">kWh</span></p>
          </div>
          <div>
            <p className="text-xs text-green-700 font-medium uppercase mb-1">Money Saved</p>
            <p className="text-3xl font-bold text-green-900">${gamificationData.savings_usd.toFixed(4)} <span className="text-sm font-medium text-green-700">USD</span></p>
          </div>
        </div>
      </div>

      {/* Leaderboard */}
      <div className="lg:col-span-2 bg-white rounded-lg shadow border border-gray-100 overflow-hidden flex flex-col h-full max-h-[400px]">
        <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-800">Community Leaderboard</h3>
        </div>
        
        <div className="overflow-y-auto flex-grow">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 text-gray-500 sticky top-0 z-10 shadow-sm">
              <tr>
                <th className="px-6 py-3 font-medium">Rank</th>
                <th className="px-6 py-3 font-medium">Device ID</th>
                <th className="px-6 py-3 font-medium">Profile</th>
                <th className="px-6 py-3 font-medium text-right">Score</th>
                <th className="px-6 py-3 font-medium text-center">Standard</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {leaderboard.map((entry) => {
                const isSelected = selectedDevice === entry.entity_id;
                
                let badgeColor = 'bg-gray-100 text-gray-600';
                if (entry.cluster_label === 'Water Guardians') badgeColor = 'bg-blue-100 text-blue-700';
                if (entry.cluster_label === 'Conscious Users') badgeColor = 'bg-yellow-100 text-yellow-700';
                if (entry.cluster_label === 'Green Opportunity') badgeColor = 'bg-orange-100 text-orange-700';

                return (
                  <tr key={entry.entity_id} className={`transition-colors ${isSelected ? 'bg-indigo-50 border-l-4 border-indigo-500' : 'hover:bg-gray-50 border-l-4 border-transparent'}`}>
                    <td className="px-6 py-3 font-bold text-gray-500">#{entry.rank}</td>
                    <td className="px-6 py-3 font-mono font-medium text-gray-800">
                      {entry.entity_id.replace('synthetic_', '')}
                      {isSelected && <span className="ml-2 text-xs font-bold text-indigo-600">(You)</span>}
                    </td>
                    <td className="px-6 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${badgeColor}`}>
                        {entry.cluster_label}
                      </span>
                    </td>
                    <td className="px-6 py-3 font-bold text-gray-800 text-right">
                      {entry.optimization_score.toFixed(1)}
                    </td>
                    <td className="px-6 py-3 text-center">
                      {entry.injunctive_norm ? (
                        <svg className="w-5 h-5 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
                      ) : (
                        <span className="text-gray-300">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
              {leaderboard.length === 0 && (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500">
                    No leaderboard data. Run Phase 2 Clustering.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default GamificationPanel;
