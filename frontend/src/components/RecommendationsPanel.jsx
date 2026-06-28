import React from 'react';

const RecommendationsPanel = ({ recommendationData }) => {
  if (!recommendationData) return null;

  return (
    <div className="bg-white rounded-lg shadow border border-gray-100 overflow-hidden mt-8">
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50 flex items-center gap-2">
        <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path></svg>
        <h3 className="text-lg font-semibold text-gray-800">Actionable Recommendations</h3>
      </div>
      <div className="p-6">
        {recommendationData.all && recommendationData.all.length > 0 ? (
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendationData.all.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 border border-gray-100">
                <div className="mt-0.5 text-indigo-500">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
                </div>
                <p className="text-sm text-gray-700">{rec}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">No recommendations available.</p>
        )}
      </div>
    </div>
  );
};

export default RecommendationsPanel;
