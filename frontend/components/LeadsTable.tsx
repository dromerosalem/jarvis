import React from 'react';
import { Lead } from '../utils/api';

// Props interface for the LeadsTable component
interface LeadsTableProps {
  leads: Lead[];
  loading: boolean;
}

/**
 * Table component for displaying leads
 * 
 * Shows all lead information in a sortable, filterable table
 */
const LeadsTable: React.FC<LeadsTableProps> = ({ leads, loading }) => {
  // If loading, show a loading spinner
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <svg className="animate-spin h-10 w-10 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    );
  }

  // If no leads, show a message
  if (leads.length === 0) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">No leads found</h3>
        <p className="mt-2 text-sm text-gray-500">
          Use the form above to search for new leads.
        </p>
      </div>
    );
  }

  // Render the table with leads
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Business
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Category
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contact
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Website
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Priority
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {leads.map((lead) => (
            <tr key={lead.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                <div className="text-sm text-gray-500">{lead.address || 'N/A'}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{lead.category || 'Unknown'}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{lead.phone || 'No phone listed'}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {lead.website ? (
                  <a 
                    href={lead.website} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    Visit Site
                  </a>
                ) : (
                  <span className="text-gray-500">No website</span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {!lead.has_website ? (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                    High
                  </span>
                ) : (
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    Low
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LeadsTable; 