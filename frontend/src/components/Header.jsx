import React from 'react';

const Header = ({ connectionStatus, lastUpdated }) => {
  return (
    <header className="bg-gray-900 text-white p-6 shadow-md flex justify-between items-center">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Energy Awareness System</h1>
        <p className="text-sm text-gray-400 mt-1">MDU Smart Room — Live Monitoring</p>
      </div>
      <div className="flex flex-col items-end">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-300">Status:</span>
          {connectionStatus === 'Connected' ? (
            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium border border-green-500/30">
              Connected
            </span>
          ) : (
            <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-xs font-medium border border-red-500/30">
              Disconnected
            </span>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Last updated: {lastUpdated ? lastUpdated : 'Never'}
        </p>
      </div>
    </header>
  );
};

export default Header;
