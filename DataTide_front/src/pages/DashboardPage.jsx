import React, { useState, useMemo, useEffect } from 'react';
import ChartComponent from '../components/ChartComponent';
import BumpChartComponent from '../components/BumpChartComponent';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import ResultsTable from '../components/ResultsTable';
import ChatbotWindow from '../components/ChatbotWindow'; // Import ChatbotWindow
import { generateMockData, generateBumpChartData, generateMockChartData, convertToCSV, downloadFile } from '../utils/index.js';
import { fetchFisheriesData } from '../api';
import { FISH_ITEMS, ANALYSIS_OPTIONS, DATA_CATEGORIES } from '../constants';
import './DashboardPage.css';
import '../styles/theme.css';
import '../components/Filter.css';
import '../components/Table.css';
import '../components/Chart.css';
import '../styles/responsive.css';
import '../components/ChatbotIcon.css';
import '../components/ChatbotWindow.css'; // Import ChatbotWindow CSS

// 환경변수에서 API 베이스 URL 가져오기
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'



export default function DashboardPage() {
  // 날짜 관련 변수는 여기에서 선언!
  const [period, setPeriod] = useState({
    startYear: new Date().getFullYear(),
    startMonth: 1,
    endYear: new Date().getFullYear(),
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
  const [selectedCategories, setSelectedCategories] = useState(['생산', '판매', '수입']) // 다중 선택
  const [tableData, setTableData] = useState([])
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isChatbotOpen, setChatbotOpen] = useState(false); // 챗봇 상태 추가
  const [bumpChartData, setBumpChartData] = useState(null);
  
  useEffect(() => {
  const bumpData = generateBumpChartData();
  setBumpChartData(bumpData);
                    }, []);


  // 검색 가능 여부 확인
  const canSearch = useMemo(() => {
    return selectedItem && selectedAnalysis && selectedCategories.length > 0
  }, [selectedItem, selectedAnalysis, selectedCategories])

  // 데이터 가져오기 함수
  async function fetchData() {
    if (!canSearch) return

    // Date validation for '통계' analysis
    if (selectedAnalysis === '통계') {
      const totalMonths = (period.endYear - period.startYear) * 12 + (period.endMonth - period.startMonth) + 1;
      if (totalMonths > 13) {
        alert('최대 1년까지 조회 가능합니다.');
        return;
      }
    }

    try {
      setLoading(true)
      setError('')
      setChartData(null); // 검색 시작 시 차트 초기화
      
      // 실제 API 호출로 변경 (주석 처리)
      // const selectedItemName = FISH_ITEMS.find(f => f.id === selectedItem)?.name; // Changed to .name
      // if (!selectedItemName) { 
      //   throw new Error('Selected item name not found.');
      // }
      // const result = await fetchFisheriesData({  
      //   selectedItem: selectedItemName,          
      //   selectedAnalysis,                        
      //   selectedCategories,                      
      //   period                                   
      // });                                        
      // setTableData(result.tableData);            
      // setChartData(result.chartData);           

      // 임시 모킹 데이터 사용 (주석 해제)
      const mockData = generateMockData(); // This is for table data
      setTableData(mockData);

      // This is for chart data
      const mockChartData = generateMockChartData({ 
        analysisType: selectedAnalysis, 
        period, 
        selectedCategories 
      });
      console.log('Generated mockChartData:', mockChartData);
      setChartData(mockChartData);

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

  const toggleChatbot = () => {
    setChatbotOpen(!isChatbotOpen);
  };

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
            📈 {FISH_ITEMS.find(f => f.id === selectedItem)?.kr_name} {selectedAnalysis} 분석 결과
            {selectedAnalysis === '통계' && (
              period.startYear === period.endYear
                ? ` (${period.startYear}년)`
                : ` (${period.startYear}~${period.endYear}년)`
            )}
          </h3>
          <div className="chart-description">
            {selectedAnalysis === '통계' ? 
              '• 올해 데이터: 선 그래프  • 전년 데이터: 막대 그래프 ' :
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

      {bumpChartData && (
        <section className="chart-section">
          <h3>📊 품목 순위 변화 (Bump Chart)</h3>
          <BumpChartComponent data={bumpChartData} />
        </section>
      )}

      <ResultsTable 
        tableData={tableData}
        loading={loading}
        selectedItem={FISH_ITEMS.find(f => f.id === selectedItem)?.kr_name}
        selectedAnalysis={selectedAnalysis}
        downloadCSV={downloadCSV}
        downloadExcel={downloadExcel}
        apiBaseUrl={API_BASE}
        selectedCategories={selectedCategories}
      />

      {/* Chatbot Icon */}
      <div className="chatbot-icon" onClick={toggleChatbot}>
        <svg viewBox="0 0 24 24">
          <path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V4c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"></path>
        </svg>
      </div>

      {/* Chatbot Window */}
      {isChatbotOpen && <ChatbotWindow onClose={toggleChatbot} />}
    </div>
  );
}