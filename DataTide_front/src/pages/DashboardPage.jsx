import React, { useState, useMemo, useEffect } from 'react';
import ChartComponent from '../components/ChartComponent';
import BumpChartComponent from '../components/BumpChartComponent';
import ScatterChartComponent from '../components/ScatterChartComponent';
import BubbleChartComponent from '../components/BubbleChartComponent';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import ResultsTable from '../components/ResultsTable';
import ChatbotWindow from '../components/ChatbotWindow'; // Import ChatbotWindow
import { generateBubbleChartData, generateScatterChartData, generateBumpChartData, generateMockChartData, convertToCSV, downloadFile } from '../utils/index.js';
import { fetchFisheriesData } from '../api';
import { ANALYSIS_OPTIONS, DATA_CATEGORIES } from '../constants';
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

const itemNameMap = {
  'Mackerel': '고등어',
  'CutlassFish': '갈치',
  'Calamari': '오징어',
};


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
  const [fishItems, setFishItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState('') // 단일 선택
  const [selectedAnalysis, setSelectedAnalysis] = useState('') // 단일 선택
  const [selectedCategories, setSelectedCategories] = useState(['생산', '판매', '수입']) // 다중 선택
  const [tableData, setTableData] = useState([])
  const [chartData, setChartData] = useState(null)
  const [chartOptions, setChartOptions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isChatbotOpen, setChatbotOpen] = useState(false); // 챗봇 상태 추가
  const [bumpChartData, setBumpChartData] = useState(null);
  const [scatterChartData, setScatterChartData] = useState(null);
  const [bubbleChartData, setBubbleChartData] = useState(null);

  const [appliedCategories, setAppliedCategories] = useState(['생산', '판매', '수입']);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/items/`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const formattedItems = data.map(item => ({
          name: item.item_name,
          kr_name: itemNameMap[item.item_name] || item.item_name,
        }));
        setFishItems(formattedItems);
      } catch (error) {
        console.error("Failed to fetch items:", error);
        // Optionally set an error state here
      }
    };

    fetchItems();
  }, []);

  useEffect(()=>{
    setChartData(null);
  }, [selectedAnalysis]);

  useEffect(() => {
  const bubbleData = generateBubbleChartData();
  setBubbleChartData(bubbleData);
                    }, []);

  useEffect(() => {
  const bumpData = generateBumpChartData();
  setBumpChartData(bumpData);
                    }, []);
  
  //// 스켈터 차트
  useEffect(() => {
  const scatterData = generateScatterChartData();
  setScatterChartData(scatterData);
                    }, []);
  ////

  // 검색 가능 여부 확인
  const canSearch = useMemo(() => {
    return selectedItem && selectedAnalysis && selectedCategories.length > 0
  }, [selectedItem, selectedAnalysis, selectedCategories])

  // 데이터 가져오기 함수
  async function fetchData() {
    if (!canSearch) return

    // Date validation for '통계' analysis
    if (selectedAnalysis === '통계') {
      if (period.startYear === period.endYear && period.startMonth > period.endMonth) {
        alert('시작 월은 종료 월보다 이전이어야 합니다.');
        return;
      }
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
      setChartOptions(null);
      setAppliedCategories(selectedCategories);
      
      const result = await fetchFisheriesData({  
        selectedItem: selectedItem,          
        selectedAnalysis,
        selectedCategories,
        period,
        base_date: '2025-08-01' // base_date for prediction
      });

      setTableData(result.tableData);

      if (selectedAnalysis === '통계') {
        const lineStyles = {
          '생산': { type: 'bar', order: 1, backgroundColor: '#006AC0', borderColor:'#ffffffff', borderWidth: 1 },
          '판매': { type: 'bar', order: 1, backgroundColor: '#FFDE47', borderColor:'#ffffffff', borderWidth: 1 },
          '수입': { type: 'bar', order: 1, backgroundColor: '#FF8410', borderColor:'#ffffffff', borderWidth: 1 },
        };
        const barStyles = {
          '생산': { type: 'line', tension:0.35, fill:true, order: 2, borderColor: '#ffffffff', backgroundColor: '#4acfc6ff', borderWidth: 1 },
          '판매': { type: 'line', tension:0.35, fill:true, order: 2, borderColor: '#ffffffff' , backgroundColor: '#b5e7f1ff', borderWidth: 1},
          '수입': { type: 'line', tension:0.35, fill:true, order: 2, borderColor: '#ffffffff', backgroundColor:'#abcddfff', borderWidth: 1},
        };

        // Use labels from the API response
        const chartLabels = result.chartData.length > 0 ? result.chartData[0].x : [];

        const formattedDatasets = result.chartData.map(trace => {
            const isBar = trace.type === 'bar'; // Use the type from the backend
            const categoryMatch = trace.name.match(/\(([^)]+)\)/);
            const category = categoryMatch ? categoryMatch[1] : '생산';
            // The original code had styles inverted, this is now corrected.
            const styles = isBar ? lineStyles[category] : barStyles[category];
            
            // For bar charts, transform data to [0, value] for floating effect
            const data = isBar ? trace.y.map(val => [0, val]) : trace.y;

            return { ...trace, ...styles, label: trace.name, data: data };
        });
        setChartData({ labels: chartLabels, datasets: formattedDatasets });

      } else { // '예측' case
        const pastTraces = result.chartData.filter(t => t.name.startsWith('과거'));
        const predictTraces = result.chartData.filter(t => t.name.startsWith('예측'));
        
        const allX = [...new Set([...pastTraces.flatMap(t => t.x), ...predictTraces.flatMap(t => t.x)])].sort();
        const ticktext = allX.map((label, index) => {
          const [year, month] = label.split('-');
          if (index === 0) return `${year}년 ${month}월`;
          const [prevYear] = allX[index - 1].split('-');
          if (year !== prevYear) return `${year}년 ${month}월`;
          return `${month}월`;
        });

        const predictionChartJsData = {
          labels: allX,
          datasets: []
        };

        const categoryMap = {
          '생산': { color: '#5C6BC0', fill: 'rgba(92, 107, 192, 0.1)' },
          '판매': { color: '#7CB342', fill: 'rgba(124, 179, 66, 0.1)' },
          '수입': { color: '#FF8A65', fill: 'rgba(255, 138, 101, 0.1)' }
        };

        selectedCategories.forEach(category => {
          const pastTrace = pastTraces.find(t => t.name.includes(category));
          const predictTrace = predictTraces.find(t => t.name.includes(category));

          if (pastTrace && predictTrace) {
            const { color, fill } = categoryMap[category];
            
            const pastDataMap = new Map(pastTrace.x.map((date, i) => [date, pastTrace.y[i]]));
            const pastY = allX.map(label => pastDataMap.get(label) || null).slice(0, pastTrace.x.length);

            const predictDataMap = new Map(predictTrace.x.map((date, i) => [date, predictTrace.y[i]]));
            const predictedY = allX.map(label => predictDataMap.get(label) || null).slice(pastTrace.x.length);

            // Past data connected to predicted
            predictionChartJsData.datasets.push({
              label: `과거 ${category}`,
              data: [...pastY.slice(0, -1), pastY[pastY.length-1], predictedY[0], ...Array(predictedY.length - 1).fill(null)],
              borderColor: color,
              backgroundColor: color,
              fill: false,
              type: 'line',
              tension: 0.1,
              pointRadius: 6,
              pointHoverRadius: 7,
              borderWidth:3.5,
            });

            // Predicted data
            predictionChartJsData.datasets.push({
              label: `예측 ${category}`,
              data: [...Array(pastY.length).fill(null), ...predictedY],
              borderColor: color,
              backgroundColor: 'transparent',
              borderDash: [5,5],
              fill: false,
              type: 'line',
              tension: 0.1,
              pointRadius: 12,
              pointHoverRadius: 15,
              pointBorderWidth: 5,
              pointBorderColor: color,
            });

            // Confidence Interval - upper bound
            predictionChartJsData.datasets.push({
              label: `신뢰구간(${category})`,
              data: [...Array(pastY.length).fill(null), ...predictedY.map(y => y ? y * 1.2 : null)],
              borderColor: 'transparent',
              backgroundColor: 'transparent',
              pointRadius: 0,
              fill: false,
            });

            // Confidence Interval - lower bound
            predictionChartJsData.datasets.push({
              label: `신뢰구간(${category})`,
              data: [...Array(pastY.length).fill(null), ...predictedY.map(y => y ? y * 0.8 : null)],
              borderColor: 'transparent',
              backgroundColor: fill,
              pointRadius: 0,
              fill: '-1', // Fill to previous dataset (upper bound)
            });
          }
        });

        const predictionChartJsOptions = {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
              line: {
                  borderWidth: 8
              }
          },
          plugins: {
            legend: {
              position: 'top',
              align: 'end',
              onClick: function(e, legendItem, legend) {
                  const chart = legend.chart;
                  const index = legendItem.datasetIndex;
                  const meta = chart.getDatasetMeta(index);
                  const newHiddenState = meta.hidden === null ? !chart.data.datasets[index].hidden : null;
                  const groupStartIndex = Math.floor(index / 4) * 4;
                  const linkedIndices = [groupStartIndex, groupStartIndex + 1, groupStartIndex + 2, groupStartIndex + 3];
                  linkedIndices.forEach(function(i) {
                      const datasetMeta = chart.getDatasetMeta(i);
                      if (datasetMeta) {
                          datasetMeta.hidden = newHiddenState;
                      }
                  });
                  chart.update();
              },
              labels: {
                  filter: function(legendItem) {
                      return !legendItem.text.includes('신뢰구간');
                  }
              }
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            },
            datalabels: {
              display: function(context) {
                const datasetLabel = context.dataset.label;
                return (datasetLabel.includes('과거') || datasetLabel.includes('예측'));
              },
              align: 'top',
              color: 'black',
              padding:{bottom:15},
              font: {
                size: 15
              },
              formatter: Math.round
            }
          },
          scales: {
            x: {
              ticks: {
                  callback: function(value, index) {
                      return ticktext[index];
                  },
                  font: {
                      weight: 'bold'
                  }
              }
            },
            y: {
              title: {
                  display: true,
                  text: '단위(톤)',
                  font: {
                      size: 15
                  }
              }
            },
          },
        };
        
        setChartData(predictionChartJsData);
        setChartOptions(predictionChartJsOptions);
      }

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
    const params = new URLSearchParams();
    params.append('type', selectedAnalysis);
    params.append('items', selectedItem);

    if (selectedAnalysis === '예측') {
      params.append('base_date', '2025-07-30');
    } else if (selectedAnalysis === '통계') {
      params.append('start', period.startYear);
      params.append('end', period.endYear);
    }

    window.open(`${API_BASE}/api/download/excel?${params.toString()}`, '_blank');
  }

  const toggleChatbot = () => {
    setChatbotOpen(!isChatbotOpen);
  };

  return (
    <div className="app-container">
      <Header />

      <SearchBar
        fishItems={fishItems}
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
          <h2>
            📈 {fishItems.find(f => f.name === selectedItem)?.kr_name} {selectedAnalysis}
            {selectedAnalysis === '통계' && (
              period.startYear === period.endYear
                ? ` (${period.startYear}년)`
                : ` (${period.startYear}~${period.endYear}년)`
            )}
          </h2>
          <div className="chart-description">
            {selectedAnalysis === '통계' ? 
              '  • 선택기간: 막대 그래프            • 전년동기: 선 그래프 ' :
              '• 실제 데이터: 실선 • 예측 데이터: 점선 + 신뢰구간'
            }
          </div>
          <ChartComponent 
            data={chartData} 
            analysisType={selectedAnalysis}
            options={chartOptions}
            selectedCategories={appliedCategories}
          />
          {selectedAnalysis === '통계' &&(
            <>
            
            {bumpChartData && (
              <section className="chart-section">
                <h3>📊 품목 순위 변화 (Bump Chart)</h3>
                <BumpChartComponent data={bumpChartData} />
              </section>
            )}
{/* 
            스켈터 차트
            {scatterChartData && (
              <section className="chart-section">
                <h3>📊 산포도 (Scatter Chart)</h3>
                <ScatterChartComponent data={scatterChartData} />
              </section>
            )}

            버블 차트
            {bubbleChartData && (
              <section className="chart-section">
                <h3>📊 포도송이 (Bubble Chart)</h3>
                <BubbleChartComponent data={bubbleChartData} />
              </section>
            )} */}
            
            </>
          )}
        </section>
      )}


      <ResultsTable 
        tableData={tableData}
        loading={loading}
        selectedItem={fishItems.find(f => f.name === selectedItem)?.kr_name}
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