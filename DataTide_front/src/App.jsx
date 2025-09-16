import React, { useState, useMemo } from 'react';
import ChartComponent from './components/ChartComponent';
import './styles/app.css';

// 환경변수에서 API 베이스 URL 가져오기
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

// 선택 옵션들 (단일 선택)
const FISH_ITEMS = [
  { id: 'KDFSH01', name: '고등어' },
  { id: 'KDFSH02', name: '갈치' },
  { id: 'KDFSH03', name: '오징어' },
  { id: 'KDFSH04', name: '명태' },
  { id: 'KDFSH05', name: '마른멸치' },
  { id: 'KDFSH06', name: '참조기' },
  { id: 'KDFSH07', name: '삼치' },
  { id: 'KDFSH08', name: '광어' },
  { id: 'KDFSH09', name: '우럭' },
  { id: 'KDFSH10', name: '전복' },
  { id: 'KDFSH11', name: '김' },
  { id: 'KDFSH12', name: '굴' },
  { id: 'KDFSH13', name: '미역' },
  { id: 'KDFSH14', name: '홍합' },
  { id: 'KDFSH15', name: '뱀장어' }
]
const ANALYSIS_OPTIONS = ['통계', '예측'] // 단일 선택
const DATA_CATEGORIES = ['생산', '판매', '수입'] // 다중 선택


export default function App() {
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
  const [yearRange, setYearRange] = useState({ start: 2015, end: currentYear })
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

      // 🔥 실제 API 호출 부분 - 시계열 데이터 서버 연동
      /*
      const params = new URLSearchParams()
      params.append('item', selectedItem)
      params.append('analysis_type', selectedAnalysis)
      params.append('categories', selectedCategories.join(','))
      if (selectedAnalysis === '통계') {
        params.append('start_year', yearRange.start)
        params.append('end_year', yearRange.end)
      } else {
        params.append('base_date', '2025-07-30')
      }

      const response = await fetch(`${API_BASE}/api/fisheries-analysis?${params}`)
      if (!response.ok) throw new Error(`API 오류: ${response.status}`)
      const result = await response.json()
      */

      // 임시 모킹 데이터
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
    setYearRange({ start: 2015, end: 2024 })
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
      {/* 헤더 */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-placeholder">
            <div className="logo-box">LOGO</div>
            <h1>수산물 유통 예측 시스템</h1>
          </div>
        </div>
      </header>

      {/* 필터 섹션 */}
      <section className="filter-section">
        <div className="filter-container">
          
          {/* 품목 선택 (단일선택, 가로배치) */}
          <div className="filter-row">
            <label className="filter-label">품목</label>
            <div className="filter-options horizontal">
              {FISH_ITEMS.map(item => (
                <button
                  key={item.id}
                  className={`option-btn ${selectedItem === item.id ? 'selected' : ''}`}
                  onClick={() => setSelectedItem(item.id)} 
                >
                  {item.name}
                </button>
              ))}
            </div>
          </div>

          {/* 분석 유형 (통계/예측, 단일선택, 가로배치) */}
          <div className="filter-row">
            <label className="filter-label">동향</label>
            <div className="filter-options horizontal">
              {ANALYSIS_OPTIONS.map(option => (
                <button
                  key={option}
                  className={`option-btn trend-button ${selectedAnalysis === option ? 'selected' : ''}`}
                  onClick={() => setSelectedAnalysis(option)}
                >
                  {option}
                </button>
              ))}
              <div className="category-group">
                {DATA_CATEGORIES.map(category => (
                  <button
                    key={category}
                    className={`option-btn trend-button small ${selectedCategories.includes(category) ? 'selected' : ''}`}
                    onClick={() => {
                      if (selectedCategories.includes(category)) {
                        setSelectedCategories(prev => prev.filter(c => c !== category))
                      } else {
                        setSelectedCategories(prev => [...prev, category])
                      }
                    }}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="filter-row hint-row">
            <small className="filter-hint">* '생산', '판매', '수입'은 다중 선택이 가능합니다.</small>
          </div>
          

          {/* 기간 선택 (통계/예측 구분 없이) */}
          {selectedAnalysis === '통계' && (
            <div className="filter-row">
              <label className="filter-label">기간</label>
              <div className="period-controls">
                <select
                  className="period-select"
                  value={period.startYear}
                  onChange={e => {
                    const val = parseInt(e.target.value, 10);
                    setPeriod(prev => ({ ...prev, startYear: val, endYear: Math.max(val, prev.endYear) }));
                  }}
                >
                  {yearOptions.map(year => (
                    <option key={year} value={year}>{year}년</option>
                  ))}
                </select>
                <select
                  className="period-select"
                  value={period.startMonth}
                  onChange={e => setPeriod(prev => ({ ...prev, startMonth: parseInt(e.target.value, 10) }))}
                >
                  {Array.from({length: 12}, (_,i) => i+1).map(month => (
                    <option key={month} value={month}>{month}월</option>
                  ))}
                </select>
                <span>~</span>
                <select
                  className="period-select"
                  value={period.endYear}
                  onChange={e => {
                    const val = parseInt(e.target.value, 10);
                    setPeriod(prev => ({ ...prev, endYear: val, startYear: Math.min(val, prev.startYear) }));
                  }}
                >
                  {yearOptions.filter(year => year >= period.startYear).map(year => (
                    <option key={year} value={year}>{year}년</option>
                  ))}
                </select>
                <select
                  className="period-select"
                  value={period.endMonth}
                  onChange={e => setPeriod(prev => ({ ...prev, endMonth: parseInt(e.target.value, 10) }))}
                >
                  {Array.from({length: 12}, (_,i) => i+1).map(month => (
                    <option key={month} value={month}>{month}월</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          </div>

          {/* 예측 정보 (예측일 때만 표시) */}
          {selectedAnalysis === '예측' && (
            <div className="prediction-info">
              <p><strong>기준일:</strong> 2025-07-30</p>
              <p><strong>과거 데이터:</strong> 6개월 (2025년 1월 ~ 7월)</p>
              <p><strong>예측 데이터:</strong> 6개월 (2025년 8월 ~ 2026년 1월)</p>
            </div>
          )}


          {/* 검색 버튼 */}
          <div className="search-section">
            <button
              type="button"
              className="option-btn reset-btn"
              onClick={resetAll}
            >
              선택초기화
            </button>
            <button
              className="option-btn primary-action-btn"
              onClick={fetchData}
              disabled={!canSearch || loading}
            >
              <span className="search-icon">🔍</span>
              {loading ? '분석 중...' : '검색하기'}
            </button>
          </div>

          {/* 오류 메시지 */}
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}
      </section>

      {/* 차트 영역 */}
      {chartData && (
        <section className="chart-section">
          <h3>
            📈 {selectedItem} {selectedAnalysis} 분석 결과
            {selectedAnalysis === '통계' && ` (${yearRange.start}~${yearRange.end}년)`}
          </h3>
          <div className="chart-description">
            {selectedAnalysis === '통계' ? 
              '• 올해 데이터: 선 그래프 (파란색) • 전년 데이터: 막대 그래프 (회색)' :
              '• 실제 데이터: 실선 (검은색) • 예측 데이터: 점선 (빨간색) + 신뢰구간'
            }
          </div>
          <ChartComponent 
            data={chartData} 
            analysisType={selectedAnalysis}
            categories={selectedCategories}
          />
        </section>
      )}

      {/* 결과 테이블 */}
      <section className="results-section">
        <div className="results-header">
          <h3>📋 상세 데이터 ({tableData.length}건)</h3>
          <div className="download-buttons">
            <button className="download-btn" onClick={downloadCSV}>
              📄 CSV 다운로드
            </button>
            <button className="download-btn" onClick={downloadExcel}>
              📗 Excel 다운로드
            </button>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                {selectedAnalysis === '통계' ? (
                  <>
                    <th>년도</th>
                    <th>품목</th>
                    <th>생산량</th>
                    <th>판매량</th>
                    <th>수입량(톤)</th>
                    <th>전년생산량</th>
                    <th>전년판매량</th>
                    <th>전년수입량</th>
                    <th>생산증감률(%)</th>
                    <th>판매증감률</th>
                    <th>수입증감률</th>
                  </>
                ) : (
                  <>
                    <th>년월</th>
                    <th>품목</th>
                    <th>생산량(톤)</th>
                    <th>판매량(톤)</th>
                    <th>수입량(톤)</th>
                    <th>데이터구분</th>
                    <th>신뢰도(%)</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {tableData.length === 0 ? (
                <tr>
                  <td colSpan={11}>{loading ? '데이터를 불러오는 중...' : '품목과 동향을 선택하고 검색하세요'}</td>
                </tr>
              ) : (
                tableData.map((row, idx) => (
                  <tr key={idx}>
                    <td>{row.period}</td>
                    <td>{selectedItem}</td>
                    <td>{formatNumber(row.production)}</td>
                    <td>{formatNumber(row.sales)}</td>
                    <td>{formatNumber(row.imports)}</td>
                    {selectedAnalysis === '통계' ? (
                      <>
                        <td>{formatNumber(row.prevProduction)}</td>
                        <td>{formatNumber(row.prevSales)}</td>
                        <td>{formatNumber(row.prevImports)}</td>
                        <td>{formatPercent(row.productionChange)}</td>
                        <td>{formatPercent(row.salesChange)}</td>
                        <td>{formatPercent(row.importsChange)}</td>
                      </>
                    ) : (
                      <>
                        <td>{row.dataType}</td>
                        <td>{row.confidence ? `${row.confidence}%` : '-' }</td>
                      </>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 🔥 시계열 데이터 서버 연동 표시 */}
        <div className="data-source-info">
          <p><strong>데이터 소스:</strong> {selectedAnalysis === '통계' ? '과거 시계열 분석 모델' : 'LSTM 기반 AI 예측 모델'}</p>
          <p><strong>서버 API:</strong> {API_BASE}/api/fisheries-analysis</p>
          <p><strong>업데이트 주기:</strong> 매월 1일 자동 갱신</p>
          <p><strong>데이터 저장:</strong> MySQL 시계열 테이블에 저장 후 분석</p>
        </div>
      </section>
    </div>
  );
}

// 모킹 데이터 생성
function generateMockData() {
  const data = []
  const periods = ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06']
  
  periods.forEach(period => {
    data.push({
      period,
      production: Math.floor(Math.random() * 5000) + 3000,
      sales: Math.floor(Math.random() * 4000) + 2500,
      imports: Math.floor(Math.random() * 2000) + 800,
      prevProduction: Math.floor(Math.random() * 4500) + 2800,
      prevSales: Math.floor(Math.random() * 3800) + 2200,
      prevImports: Math.floor(Math.random() * 1800) + 700,
      productionChange: (Math.random() - 0.5) * 30,
      salesChange: (Math.random() - 0.5) * 25,
      importsChange: (Math.random() - 0.5) * 40,
      dataType: period > '2024-03' ? '예측' : '실제',
      confidence: period > '2024-03' ? Math.floor(Math.random() * 15) + 80 : null
    })
  })
  
  return data
}

function generateMockChartData() {
  return {
    labels: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06'],
    current: [3200, 3400, 3100, 3600, 3800, 3500],
    previous: [3000, 3200, 2900, 3400, 3500, 3300],
    predicted: [null, null, null, 3600, 3800, 3500]
  }
}

// 유틸리티 함수들
function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return new Intl.NumberFormat('ko-KR').format(value)
}

function formatPercent(value) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}

function getChangeClass(value) {
  if (value > 0) return 'positive-change'
  if (value < 0) return 'negative-change'
  return ''
}

function convertToCSV(data) {
  const headers = ['기간', '생산량', '판매량', '수입량']
  const csvContent = [
    headers.join(','),
    ...data.map(row => [
      row.period, row.production, row.sales, row.imports
    ].join(','))
  ].join('\n')
  
  return '\uFEFF' + csvContent
}

function downloadFile(content, fileName, contentType) {
  const blob = new Blob([content], { type: contentType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  window.URL.revokeObjectURL(url)
}
