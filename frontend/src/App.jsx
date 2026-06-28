import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DeviceList from './components/DeviceList';
import AlgorithmMetricsPanel from './components/AlgorithmMetricsPanel';
import Phase2ValidationPanel from './components/Phase2ValidationPanel';
import SummaryHeader from './components/SummaryHeader';
import RecommendationsPanel from './components/RecommendationsPanel';
import GamificationPanel from './components/GamificationPanel';
import ThesisValidationPanel from './components/ThesisValidationPanel';

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [lights, setLights] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [activeTab, setActiveTab] = useState('live'); // 'live' or 'validation'
  
  // Gamification & Recommendation state
  const [gamification, setGamification] = useState({});
  const [recommendations, setRecommendations] = useState({});

  const fetchData = async () => {
    try {
      const [lightsRes, metricsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/lights`),
        fetch(`${API_BASE_URL}/metrics`)
      ]);

      if (!lightsRes.ok || !metricsRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const lightsData = await lightsRes.json();
      const metricsData = await metricsRes.json();

      setLights(lightsData);
      setMetrics(metricsData);
      setConnectionStatus('Connected');
      
      const now = new Date();
      setLastUpdated(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

      // Auto-select first device on initial load if none selected
      if (!selectedDevice && lightsData.length > 0) {
        setSelectedDevice(lightsData[0].entity_id);
      }

    } catch (error) {
      console.error("API Fetch Error:", error);
      setConnectionStatus('Disconnected');
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Set interval for every 60 seconds
    const intervalId = setInterval(() => {
      fetchData();
    }, 60000);

    return () => clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run once on mount

  // Fetch Gamification and Recommendations when device changes
  useEffect(() => {
    if (!selectedDevice) return;

    const fetchDeviceExtras = async () => {
      try {
        const [gamRes, recRes] = await Promise.all([
          fetch(`${API_BASE_URL}/gamification/${selectedDevice}`),
          fetch(`${API_BASE_URL}/recommendations/${selectedDevice}`)
        ]);
        
        if (gamRes.ok && recRes.ok) {
          const gamData = await gamRes.json();
          const recData = await recRes.json();
          setGamification(prev => ({ ...prev, [selectedDevice]: gamData }));
          setRecommendations(prev => ({ ...prev, [selectedDevice]: recData }));
        }
      } catch (e) {
        console.error("Failed to fetch gamification/recommendation data", e);
      }
    };
    
    fetchDeviceExtras();
    
    // Also poll every 60s
    const id = setInterval(fetchDeviceExtras, 60000);
    return () => clearInterval(id);
  }, [selectedDevice]);

  // Find the currently selected device's metrics
  const selectedMetrics = metrics.find(m => m.entity_id === selectedDevice);
  const currentGamification = gamification[selectedDevice];
  const currentRecommendations = recommendations[selectedDevice];

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      <Header connectionStatus={connectionStatus} lastUpdated={lastUpdated} />
      
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('live')}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'live'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Live Dashboard
            </button>
            <button
              onClick={() => setActiveTab('validation')}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'validation'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Phase 2 Validation
            </button>
            <button
              onClick={() => setActiveTab('thesis')}
              className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'thesis'
                  ? 'border-violet-600 text-violet-700'
                  : 'border-transparent text-gray-500 hover:text-violet-600 hover:border-violet-300'
              }`}
            >
              🎓 Thesis Validation
            </button>
          </nav>
        </div>
      </div>

      <main className="flex-grow p-6 lg:p-8 max-w-7xl mx-auto w-full">
        {activeTab === 'live' ? (
          <div className="flex flex-col h-full">
            <SummaryHeader gamificationData={currentGamification} recommendationData={currentRecommendations} />
            
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Left Column: Device List */}
              <div className="lg:col-span-7">
                 <DeviceList 
                    devices={lights} 
                    selectedDevice={selectedDevice} 
                    onSelectDevice={setSelectedDevice} 
                 />
              </div>
              
              {/* Right Column: Metrics Panel */}
              <div className="lg:col-span-5 h-full">
                 <AlgorithmMetricsPanel metrics={selectedMetrics} />
              </div>
            </div>
            
            <RecommendationsPanel recommendationData={currentRecommendations} />
            
            <GamificationPanel selectedDevice={selectedDevice} gamificationData={currentGamification} />
          </div>
        ) : activeTab === 'validation' ? (
          <Phase2ValidationPanel />
        ) : (
          <ThesisValidationPanel />
        )}
      </main>
    </div>
  );
}

export default App;
