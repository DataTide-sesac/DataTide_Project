const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

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
  
  if (!response.ok) {
    throw new Error(`API 오류: ${response.status}`);
  }
  
  return await response.json();
}
