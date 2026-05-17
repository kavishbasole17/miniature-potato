import axios from 'axios';

// Use environment variable for API URL in production, fallback to localhost for dev
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
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

export const exportCsvUrl = `${API_BASE_URL}/api/export/csv`;
