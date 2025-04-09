import axios from 'axios';

// Define the base API URL from environment variables
const API_URL = process.env.API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define types for our API responses
export interface Lead {
  id: number;
  name: string;
  category: string | null;
  address: string | null;
  phone: string | null;
  website: string | null;
  has_website: boolean;
  source: string;
  query: string;
  created_at: string;
}

export interface ScrapeResponse {
  success: boolean;
  leads_added: number;
  high_priority: number;
}

// API functions

/**
 * Start a scraping job
 * @param query - The search query (e.g., "plumbers in Manchester")
 */
export const scrapeLeads = async (query: string): Promise<ScrapeResponse> => {
  try {
    const response = await api.post<ScrapeResponse>('/scrape-leads', { query });
    return response.data;
  } catch (error) {
    console.error('Error scraping leads:', error);
    throw error;
  }
};

/**
 * Get all leads from the database
 * @param highPriorityOnly - If true, only return leads without websites
 */
export const getLeads = async (highPriorityOnly = false): Promise<Lead[]> => {
  try {
    const response = await api.get<Lead[]>('/leads', {
      params: { high_priority_only: highPriorityOnly },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching leads:', error);
    throw error;
  }
};

export default api; 