import React from 'react';

const DeviceList = ({ devices, selectedDevice, onSelectDevice }) => {
  if (!devices || devices.length === 0) {
    return (
      <div className="p-6 bg-white rounded-lg shadow border border-gray-100 flex items-center justify-center h-48">
        <p className="text-gray-500">No devices found.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-100">
      <div className="px-6 py-4 border-b border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800">Connected Devices</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="px-6 py-3 font-medium">Device ID</th>
              <th className="px-6 py-3 font-medium">State</th>
              <th className="px-6 py-3 font-medium">Brightness</th>
              <th className="px-6 py-3 font-medium">Last Changed</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {devices.map((device) => {
              const isSelected = selectedDevice === device.entity_id;
              return (
                <tr
                  key={device.entity_id}
                  onClick={() => onSelectDevice(device.entity_id)}
                  className={`cursor-pointer transition-colors hover:bg-blue-50 ${
                    isSelected ? 'bg-blue-50 border-l-4 border-blue-500' : 'border-l-4 border-transparent'
                  }`}
                >
                  <td className="px-6 py-4 font-medium text-gray-800">{device.entity_id}</td>
                  <td className="px-6 py-4">
                    {device.state === 'on' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-green-100 text-green-700 text-xs font-semibold">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                        On
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gray-100 text-gray-600 text-xs font-semibold">
                        <span className="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                        Off
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{ width: `${device.brightness}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-500 w-8">{Math.round(device.brightness)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{device.last_changed}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DeviceList;
