import React from 'react';
import { ScrapeResponse } from '../utils/api';

// Props interface for the StatsSummary component
interface StatsSummaryProps {
  stats: ScrapeResponse | null;
}

/**
 * Component that displays statistics after a scraping job is completed
 */
const StatsSummary: React.FC<StatsSummaryProps> = ({ stats }) => {
  // If no stats are available, don't render anything
  if (!stats) {
    return null;
  }

  return (
    <div className="bg-primary-50 border border-primary-200 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-bold text-primary-800 mb-2">Scan Results</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {/* Total leads card */}
        <div className="bg-white p-4 rounded shadow-sm">
          <p className="text-sm text-gray-500">Total Leads Found</p>
          <p className="text-3xl font-bold text-gray-800">{stats.leads_added}</p>
        </div>
        
        {/* High priority leads card */}
        <div className="bg-white p-4 rounded shadow-sm">
          <p className="text-sm text-gray-500">High Priority Leads</p>
          <p className="text-3xl font-bold text-red-600">{stats.high_priority}</p>
          <p className="text-xs text-gray-500">No website found</p>
        </div>
        
        {/* Conversion rate card */}
        <div className="bg-white p-4 rounded shadow-sm">
          <p className="text-sm text-gray-500">Conversion Potential</p>
          <p className="text-3xl font-bold text-green-600">
            {stats.leads_added ? 
              `${Math.round((stats.high_priority / stats.leads_added) * 100)}%` : 
              '0%'
            }
          </p>
          <p className="text-xs text-gray-500">Businesses that need websites</p>
        </div>
      </div>
      
      <div className="mt-4 text-sm text-primary-700">
        <p>
          <strong>Pro Tip:</strong> High priority leads are businesses without websites - these are your best potential clients!
        </p>
      </div>
    </div>
  );
};

export default StatsSummary; 