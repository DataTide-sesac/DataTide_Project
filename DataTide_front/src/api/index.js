const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

async function handleApiResponse(response) {
  if (!response.ok) {
    throw new Error(`API 오류: ${response.status}`);
  }
  return await response.json();
}

export async function fetchFisheriesData(params) {
  const queryParams = new URLSearchParams();
  
  queryParams.append('item', params.selectedItem);
  queryParams.append('analysis_type', params.selectedAnalysis);
  queryParams.append('categories', params.selectedCategories.join(','));

  if (params.selectedAnalysis === '통계') {
    queryParams.append('start_year', params.period.startYear);
    queryParams.append('end_year', params.period.endYear);
  } else {
    queryParams.append('base_date', '2025-07-30');
  }

  const response = await fetch(`${API_BASE}/api/fisheries-analysis?${queryParams}`);
  return handleApiResponse(response);
}

export async function fetchPredictionDataApi(params) {
  const queryParams = new URLSearchParams();
  queryParams.append('items', params.selectedItems.join(','));
  if (params.selectedLocation) queryParams.append('location', params.selectedLocation);
  queryParams.append('base_date', params.baseDate);
  queryParams.append('type', 'prediction');

  const response = await fetch(`${API_BASE}/api/prediction-data?${queryParams}`);
  return handleApiResponse(response);
}

export async function fetchStatsDataApi(params) {
  const queryParams = new URLSearchParams();
  queryParams.append('items', params.selectedItems.join(','));
  if (params.selectedLocation) queryParams.append('location', params.selectedLocation);
  queryParams.append('start_year', params.yearRange.start);
  queryParams.append('end_year', params.yearRange.end);
  queryParams.append('type', 'stats');

  const response = await fetch(`${API_BASE}/api/stats-data?${queryParams}`);
  return handleApiResponse(response);
}

export function getExcelDownloadUrl(type, params) {
  const queryParams = new URLSearchParams();
  queryParams.append('type', type);
  queryParams.append('items', params.selectedItems.join(','));
  if (params.selectedLocation) queryParams.append('location', params.selectedLocation);

  if (type === 'prediction') {
    queryParams.append('base_date', params.baseDate);
  } else if (type === 'stats') {
    queryParams.append('start', params.yearRange.start);
    queryParams.append('end', params.yearRange.end);
  }

  return `${API_BASE}/api/download/excel?${queryParams}`;
}

export async function sendChatbotMessage(message) {
  const response = await fetch(`${API_BASE}/api/chatbot`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: message }),
  });
  return handleApiResponse(response);
}
