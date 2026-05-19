import axios from 'axios';

// Use environment variable for API URL in production, fallback to localhost for dev
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  withCredentials: true,
});

export const fetchOpportunities = async (params: any) => {
  const { data } = await api.get('/opportunities', { params });
  return data;
};

export const fetchFilterOptions = async () => {
  const { data } = await api.get('/options');
  return data;
};

export const triggerScrape = async () => {
  const { data } = await api.post('/scrape');
  return data;
};

export const exportCsvUrl = `${API_BASE_URL}/api/opportunities/export.csv`;
