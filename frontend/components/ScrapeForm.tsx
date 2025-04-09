import React, { useState } from 'react';
import { scrapeLeads, ScrapeResponse } from '../utils/api';

// Props interface for the ScrapeForm component
interface ScrapeFormProps {
  onSuccess: (response: ScrapeResponse) => void;
  onError: (error: any) => void;
}

/**
 * Form component for initiating a scraping job
 * 
 * Allows users to enter a search query and submit it to the backend
 */
const ScrapeForm: React.FC<ScrapeFormProps> = ({ onSuccess, onError }) => {
  // State for the search query input
  const [query, setQuery] = useState('');
  
  // State for tracking loading state
  const [isLoading, setIsLoading] = useState(false);
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate the input
    if (!query.trim()) {
      alert('Please enter a search query');
      return;
    }
    
    // Start loading state
    setIsLoading(true);
    
    try {
      // Call the API to start scraping
      const response = await scrapeLeads(query);
      
      // Reset the form and update parent component
      setQuery('');
      onSuccess(response);
    } catch (error) {
      // Handle errors
      onError(error);
    } finally {
      // Reset loading state
      setIsLoading(false);
    }
  };
  
  return (
    <div className="card mb-6">
      <h2 className="text-2xl font-bold mb-4">Find Local Business Leads</h2>
      <p className="text-gray-600 mb-4">
        Enter a search query like "plumbers in Manchester" to find local businesses 
        that might need your digital marketing services.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
            Search Query
          </label>
          <input
            id="query"
            type="text"
            className="input w-full"
            placeholder="e.g., plumbers in Manchester"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            Try to be specific with location and business type.
          </p>
        </div>
        
        <button
          type="submit"
          className="btn btn-primary w-full"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Scanning...
            </span>
          ) : (
            'Start Scan'
          )}
        </button>
      </form>
    </div>
  );
};

export default ScrapeForm; 