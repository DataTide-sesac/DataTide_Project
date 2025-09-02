import React, { useState, useMemo } from 'react';
import ChartComponent from '../components/ChartComponent';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import ResultsTable from '../components/ResultsTable';
import { generateMockData, generateMockChartData, convertToCSV, downloadFile } from '../utils';
import { fetchFisheriesData } from '../api';
import { FISH_ITEMS, ANALYSIS_OPTIONS, DATA_CATEGORIES } from '../constants';
import './DashboardPage.css';
import '../styles/theme.css';
import '../components/Filter.css';
import '../components/Table.css';
import '../components/Chart.css';
import '../styles/responsive.css';

// 환경변수에서 API 베이스 URL 가져오기
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function DashboardPage() {
  // 날짜 관련 변수는 여기에서 선언!
  const [period, setPeriod] = useState({
    startYear: 2015,
    startMonth: 1,
    endYear: 2024,
    endMonth: 12
  });

  const currentYear = new Date().getFullYear();
  const yearOptions = [];
  for (let year = 2015; year <= currentYear; year++) {
    yearOptions.push(year);
  }

  // 상태 관리
  const [selectedItem, setSelectedItem] = useState('') // 단일 선택
  const [selectedAnalysis, setSelectedAnalysis] = useState('') // 단일 선택
  const [selectedCategories, setSelectedCategories] = useState([]) // 다중 선택
  const [tableData, setTableData] = useState([])
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // 검색 가능 여부 확인
  const canSearch = useMemo(() => {
    return selectedItem && selectedAnalysis && selectedCategories.length > 0
  }, [selectedItem, selectedAnalysis, selectedCategories])

  // 데이터 가져오기 함수
  async function fetchData() {
    if (!canSearch) return

    try {
      setLoading(true)
      setError('')

      // 실제 API를 사용하려면 아래 주석을 해제하세요.
      // const result = await fetchFisheriesData({ selectedItem, selectedAnalysis, selectedCategories, period });
      // setTableData(result.tableData);
      // setChartData(result.chartData);

      // 임시 모킹 데이터 사용
      const mockData = generateMockData()
      const mockChartData = generateMockChartData()

      setTableData(mockData)
      setChartData(mockChartData)

    } catch (err) {
      setError(err.message || '데이터를 가져오는 중 오류가 발생했습니다')
      setTableData([])
      setChartData(null)
    } finally {
      setLoading(false)
    }
  }

  // 선택 초기화
  function resetAll() {
    setSelectedItem('')
    setSelectedAnalysis('')
    setSelectedCategories([])
    setPeriod({ startYear: 2015, startMonth: 1, endYear: 2024, endMonth: 12 })
    setTableData([])
    setChartData(null)
    setError('')
  }

  // CSV 다운로드
  function downloadCSV() {
    const csvContent = convertToCSV(tableData)
    downloadFile(csvContent, 'fisheries_data.csv', 'text/csv')
  }

  // Excel 다운로드
  function downloadExcel() {
    window.open(`${API_BASE}/api/download/excel?type=${selectedAnalysis}&item=${selectedItem}`, '_blank')
  }

  return (
    <div className="app-container">
      <Header />

      <SearchBar
        fishItems={FISH_ITEMS}
        analysisOptions={ANALYSIS_OPTIONS}
        dataCategories={DATA_CATEGORIES}
        yearOptions={yearOptions}
        period={period}
        setPeriod={setPeriod}
        selectedItem={selectedItem}
        setSelectedItem={setSelectedItem}
        selectedAnalysis={selectedAnalysis}
        setSelectedAnalysis={setSelectedAnalysis}
        selectedCategories={selectedCategories}
        setSelectedCategories={setSelectedCategories}
        fetchData={fetchData}
        resetAll={resetAll}
        canSearch={canSearch}
        loading={loading}
        error={error}
      />

      {/* 차트 영역 */}
      {chartData && (
        <section className="chart-section">
          <h3>
            📈 {FISH_ITEMS.find(f => f.id === selectedItem)?.name} {selectedAnalysis} 분석 결과
            {selectedAnalysis === '통계' && ` (${period.startYear}~${period.endYear}년)`}
          </h3>
          <div className="chart-description">
            {selectedAnalysis === '통계' ? 
              '• 올해 데이터: 선 그래프 (카테고리별 색상) • 전년 데이터: 막대 그래프 (카테고리별 색상)' :
              '• 실제 데이터: 실선 • 예측 데이터: 점선 + 신뢰구간'
            }
          </div>
          <ChartComponent 
            data={chartData} 
            analysisType={selectedAnalysis}
            selectedCategories={selectedCategories}
          />
        </section>
      )}

      <ResultsTable 
        tableData={tableData}
        loading={loading}
        selectedItem={FISH_ITEMS.find(f => f.id === selectedItem)?.name}
        selectedAnalysis={selectedAnalysis}
        downloadCSV={downloadCSV}
        downloadExcel={downloadExcel}
        apiBaseUrl={API_BASE}
      />
    </div>
  );
}