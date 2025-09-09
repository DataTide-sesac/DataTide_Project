//   주요 수정 내용:
//    1. Mock 데이터 제거 및 실제 API 연동
//    2. API 호출 시 파라미터 수정 (ID → 이름)
// -----
// // src/pages/DashboardPage.jsx
// import React, { useState, useMemo } from 'react';
// import ChartComponent from '../components/ChartComponent';
// import Header from '../components/Header';
// import SearchBar from '../components/SearchBar';
// import ResultsTable from '../components/ResultsTable';
// import ChatbotWindow from '../components/ChatbotWindow'; // Import ChatbotWindow
// import { generateMockData, convertToCSV, downloadFile } from '../utils';
// import { fetchFisheriesData } from '../api';
// import { FISH_ITEMS, ANALYSIS_OPTIONS, DATA_CATEGORIES } from '../constants';
// import './DashboardPage.css';
// import '../styles/theme.css';
// import '../components/Filter.css';
// import '../components/Table.css';
// import '../components/Chart.css';
// import '../styles/responsive.css';
// import '../components/ChatbotIcon.css';
// import '../components/ChatbotWindow.css'; // Import ChatbotWindow CSS

// // 환경변수에서 API 베이스 URL 가져오기
// const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// // 이 함수를 DashboardPage 내로 이동 또는 utils.js에 정의할 수 있습니다.
// const generateDynamicChartData = (period, categories) => {
//   const { startYear, endYear, startMonth, endMonth } = period;
//   const allMonths = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
  
//   const fullYData = {
//     current: {
//       '생산': [25, 18, 27, 38, 33, 49, 36, 40, 43, 37, 44, 47],
//       '판매': [21, 16, 25, 33, 28, 43, 32, 35, 38, 31, 39, 41],
//       '수입': [18, 13, 22, 27, 24, 38, 29, 33, 35, 28, 36, 39]
//     },
//     previous: {
//       '생산': [18, 12, 20, 30, 25, 40, 28, 32, 35, 28, 35, 38],
//       '판매': [15, 10, 18, 25, 20, 35, 25, 28, 30, 25, 30, 33],
//       '수입': [12, 8, 15, 20, 18, 30, 22, 25, 28, 22, 28, 30]
//     }
//   };

//   let monthLabels = allMonths;
//   let yData = fullYData;

//   // 사용자가 선택한 기간에 맞춰 데이터 슬라이싱
//   if (startYear === endYear && startMonth >= 1 && endMonth <= 12 && startMonth <= endMonth) {
//     monthLabels = allMonths.slice(startMonth - 1, endMonth);
//     const sliceData = (data) => data.slice(startMonth - 1, endMonth);
//     yData = {
//       current: {
//         '생산': sliceData(fullYData.current['생산']),
//         '판매': sliceData(fullYData.current['판매']),
//         '수입': sliceData(fullYData.current['수입']),
//       },
//       previous: {
//         '생산': sliceData(fullYData.previous['생산']),
//         '판매': sliceData(fullYData.previous['판매']),
//         '수입': sliceData(fullYData.previous['수입']),
//       }
//     };
//   }

//   const traces = [
//     {
//       x: monthLabels,
//       y: yData.current['생산'],
//       name: `${endYear}(생산)`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#1565C0' },
//     },
//     {
//       x: monthLabels,
//       y: yData.current['판매'],
//       name: `${endYear}(판매)`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#388E3C' },
//     },
//     {
//       x: monthLabels,
//       y: yData.current['수입'],
//       name: `${endYear}(수입)`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#F57C00' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['생산'],
//       name: `${endYear - 1}(생산)`,
//       type: 'bar',
//       marker: { color: 'rgba(100, 181, 246, 0.65)' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['판매'],
//       name: `${endYear - 1}(판매)`,
//       type: 'bar',
//       marker: { color: 'rgba(129, 199, 132, 0.65)' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['수입'],
//       name: `${endYear - 1}(수입)`,
//       type: 'bar',
//       marker: { color: 'rgba(255, 183, 77, 0.65)' },
//     },
//   ];

//   // 선택된 카테고리에 따라 필터링
//   return traces.filter(trace => {
//     const categoryMatch = trace.name.match(/\(([^)]+)\)/);
//     return categoryMatch && categories.includes(categoryMatch[1].trim());
//   });
// };

// export default function DashboardPage() {
//   // 날짜 관련 변수는 여기에서 선언!
//   const [period, setPeriod] = useState({
//     startYear: 2015,
//     startMonth: 1,
//     endYear: 2024,
//     endMonth: 12
//   });

//   const currentYear = new Date().getFullYear();
//   const yearOptions = [];
//   for (let year = 2015; year <= currentYear; year++) {
//     yearOptions.push(year);
//   }

//   // 상태 관리
//   const [selectedItem, setSelectedItem] = useState('') // 단일 선택
//   const [selectedAnalysis, setSelectedAnalysis] = useState('') // 단일 선택
//   const [selectedCategories, setSelectedCategories] = useState([]) // 다중 선택
//   const [tableData, setTableData] = useState([])
//   const [chartData, setChartData] = useState(null)
//   const [loading, setLoading] = useState(false)
//   const [error, setError] = useState('')
//   const [isChatbotOpen, setChatbotOpen] = useState(false); // 챗봇 상태 추가
  
//   // 검색 가능 여부 확인
//   const canSearch = useMemo(() => {
//     return selectedItem && selectedAnalysis && selectedCategories.length > 0
//   }, [selectedItem, selectedAnalysis, selectedCategories])

//   // 데이터 가져오기 함수
//   async function fetchData() {
//     if (!canSearch) return

//     // Date validation for '통계' analysis
//     if (selectedAnalysis === '통계') {
//       const totalMonths = (period.endYear - period.startYear) * 12 + (period.endMonth - period.startMonth) + 1;
//       if (totalMonths > 13) {
//         alert('최대 1년까지 조회 가능합니다.');
//         return;
//       }
//     }

//     try {
//       setLoading(true)
//       setError('')
//       setChartData(null); // 검색 시작 시 차트 초기화

//       // 실제 API 호출로 변경
//       const selectedItemName = FISH_ITEMS.find(f => f.id === selectedItem)?.name;
//       if (!selectedItemName) {
//         throw new Error('Selected item name not found.');
//       }
//       const result = await fetchFisheriesData({ 
//         selectedItem: selectedItemName, 
//         selectedAnalysis, 
//         selectedCategories, 
//         period 
//       });
//       setTableData(result.tableData);
//       setChartData(result.chartData);

//       // 임시 모킹 데이터 사용 (주석 처리)
//       // const mockData = generateMockData();
//       // setTableData(mockData);

//       // if (selectedAnalysis === '통계') {
//       //   const dynamicChartData = generateDynamicChartData(period, selectedCategories);
//       //   setChartData(dynamicChartData);
//       // } else {
//       //   // 예측 분석용 차트 데이터 생성 로직 (필요 시)
//       //   // const predictionChartData = generatePredictionChartData(period, selectedCategories);
//       //   // setChartData(predictionChartData);
//       // }

//     } catch (err) {
//       setError(err.message || '데이터를 가져오는 중 오류가 발생했습니다')
//       setTableData([])
//       setChartData(null)
//     } finally {
//       setLoading(false)
//     }
//   }

//   // 선택 초기화
//   function resetAll() {
//     setSelectedItem('')
//     setSelectedAnalysis('')
//     setSelectedCategories([])
//     setPeriod({ startYear: 2015, startMonth: 1, endYear: 2024, endMonth: 12 })
//     setTableData([])
//     setChartData(null)
//     setError('')
//   }

//   // CSV 다운로드
//   function downloadCSV() {
//     const csvContent = convertToCSV(tableData)
//     downloadFile(csvContent, 'fisheries_data.csv', 'text/csv')
//   }

//   // Excel 다운로드
//   function downloadExcel() {
//     window.open(`${API_BASE}/api/download/excel?type=${selectedAnalysis}&item=${selectedItem}`, '_blank')
//   }

//   const toggleChatbot = () => {
//     setChatbotOpen(!isChatbotOpen);
//   };

//   return (
//     <div className="app-container">
//       <Header />

//       <SearchBar
//         fishItems={FISH_ITEMS}
//         analysisOptions={ANALYSIS_OPTIONS}
//         dataCategories={DATA_CATEGORIES}
//         yearOptions={yearOptions}
//         period={period}
//         setPeriod={setPeriod}
//         selectedItem={selectedItem}
//         setSelectedItem={setSelectedItem}
//         selectedAnalysis={selectedAnalysis}
//         setSelectedAnalysis={setSelectedAnalysis}
//         selectedCategories={selectedCategories}
//         setSelectedCategories={setSelectedCategories}
//         fetchData={fetchData}
//         resetAll={resetAll}
//         canSearch={canSearch}
//         loading={loading}
//         error={error}
//       />

//       {/* 차트 영역 */}
//       {chartData && (
//         <section className="chart-section">
//           <h3>
//             📈 {FISH_ITEMS.find(f => f.id === selectedItem)?.name} {selectedAnalysis} 분석 결과
//             {selectedAnalysis === '통계' && ` (${period.startYear}~${period.endYear}년)`}
//           </h3>
//           <div className="chart-description">
//             {selectedAnalysis === '통계' ? 
//               '• 올해 데이터: 선 그래프  • 전년 데이터: 막대 그래프 ' :
//               '• 실제 데이터: 실선 • 예측 데이터: 점선 + 신뢰구간'
//             }
//           </div>
//           <ChartComponent 
//             data={chartData} 
//             analysisType={selectedAnalysis}
//             selectedCategories={selectedCategories}
//           />
//         </section>
//       )}

//       <ResultsTable 
//         tableData={tableData}
//         loading={loading}
//         selectedItem={FISH_ITEMS.find(f => f.id === selectedItem)?.name}
//         selectedAnalysis={selectedAnalysis}
//         downloadCSV={downloadCSV}
//         downloadExcel={downloadExcel}
//         apiBaseUrl={API_BASE}
//         selectedCategories={selectedCategories}
//       />

//       {/* Chatbot Icon */}
//       <div className="chatbot-icon" onClick={toggleChatbot}>
//         <svg viewBox="0 0 24 24">
//           <path d="M21 6h-2v9H6v2c0 .55.45 1 1 1h11l4 4V7c0-.55-.45-1-1-1zm-4 6V4c0-.55-.45-1-1-1H3c-.55 0-1 .45-1 1v14l4-4h10c.55 0 1-.45 1-1z"></path>
//         </svg>
//       </div>

//       {/* Chatbot Window */}
//       {isChatbotOpen && <ChatbotWindow onClose={toggleChatbot} />}
//     </div>
//   );
// }
