import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import ScrapeForm from '../components/ScrapeForm';
import LeadsTable from '../components/LeadsTable';
import StatsSummary from '../components/StatsSummary';
import { getLeads, Lead, ScrapeResponse } from '../utils/api';

/**
 * Main page component for the Lead Finder application
 * 
 * Combines the scrape form, stats summary, and leads table
 */
const HomePage = () => {
  // State for storing the leads
  const [leads, setLeads] = useState<Lead[]>([]);
  
  // State for tracking loading state
  const [loading, setLoading] = useState<boolean>(false);
  
  // State for storing the scrape response stats
  const [scrapeStats, setScrapeStats] = useState<ScrapeResponse | null>(null);
  
  // State for storing any error messages
  const [error, setError] = useState<string | null>(null);
  
  // State for filter (high priority only)
  const [highPriorityOnly, setHighPriorityOnly] = useState<boolean>(false);

  // Load leads on initial render and when high priority filter changes
  useEffect(() => {
    loadLeads();
  }, [highPriorityOnly]);

  // Function to load leads from the API
  const loadLeads = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await getLeads(highPriorityOnly);
      setLeads(data);
    } catch (err) {
      console.error('Error loading leads:', err);
      setError('Failed to load leads. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Handle successful scrape
  const handleScrapeSuccess = (response: ScrapeResponse) => {
    setScrapeStats(response);
    loadLeads(); // Reload leads to include the newly scraped ones
  };

  // Handle scrape error
  const handleScrapeError = (err: any) => {
    console.error('Scrape error:', err);
    setError('An error occurred while scraping. Please try again later.');
  };

  return (
    <div>
      <Head>
        <title>Jarvis Lead Finder | Find Local Business Opportunities</title>
        <meta name="description" content="Find local businesses with weak online presence that need your digital marketing services" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Jarvis Lead Finder</h1>
          <p className="text-gray-600">
            Find local businesses with weak online presence that need your digital marketing services
          </p>
        </header>
        
        {/* Form section */}
        <section>
          <ScrapeForm 
            onSuccess={handleScrapeSuccess} 
            onError={handleScrapeError} 
          />
        </section>
        
        {/* Stats summary section */}
        {scrapeStats && (
          <section>
            <StatsSummary stats={scrapeStats} />
          </section>
        )}
        
        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}
        
        {/* Leads table section */}
        <section>
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Business Leads</h2>
              
              {/* Filter toggle */}
              <div className="flex items-center">
                <label htmlFor="high-priority" className="mr-2 text-sm text-gray-700">
                  High Priority Only
                </label>
                <input
                  id="high-priority"
                  type="checkbox"
                  className="rounded text-primary-600 focus:ring-primary-500"
                  checked={highPriorityOnly}
                  onChange={(e) => setHighPriorityOnly(e.target.checked)}
                />
              </div>
            </div>
            
            {/* Leads table */}
            <LeadsTable leads={leads} loading={loading} />
          </div>
        </section>
      </main>
    </div>
  );
};

export default HomePage; 