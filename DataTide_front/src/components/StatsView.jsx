import React, { useState, useEffect } from 'react'
import ChartComponent from './ChartComponent'
import { fetchStatsDataApi, getExcelDownloadUrl } from '../api';
import { scales } from 'chart.js';

export default function StatsView({ selectedItems, selectedLocation }) {
  const [yearRange, setYearRange] = useState({ start: 2015, end: 2024 })
  const [statsData, setStatsData] = useState([])
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 연도 옵션 생성 (10년간)
  const yearOptions = []
  for (let year = 2015; year <= 2024; year++) {
    yearOptions.push(year)
  }

  // 검색 가능 여부
  const canSearch = selectedItems.length > 0

  // 통계 데이터 조회
  async function fetchStatsData() {
    if (!canSearch) return

    try {
      setLoading(true)
      setError('')

      // 실제 API 호출
      const result = await fetchStatsDataApi({
        selectedItems,
        selectedLocation,
        yearRange
      });
      const realStatsData = result.statsData || [];
      setStatsData(realStatsData);

      // 차트 데이터 가공 및 설정
      const processedChartData = processDataForChart(realStatsData);
      setChartData(processedChartData);

    } catch (err) {
      setError(err.message || '데이터를 가져오는 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  // CSV 다운로드
  function downloadCSV() {
    const csvContent = convertToCSV(statsData)
    downloadFile(csvContent, 'stats_data.csv', 'text/csv')
  }

  // Excel 다운로드
  function downloadExcel() {
    const url = getExcelDownloadUrl('stats', {
      selectedItems,
      selectedLocation,
      yearRange
    });
    window.open(url, '_blank');
  }

  return (
    <div className="stats-view">
      {/* 통계 전용 필터 */}
      <section className="stats-filter-section">
        <div className="filter-container">
          <div className="period-filter">
            <label>기간 선택 (연도)</label>
            <div className="year-range">
              <select 
                value={yearRange.start}
                onChange={(e) => setYearRange(prev => ({ ...prev, start: parseInt(e.target.value) }))}
              >
                {yearOptions.map(year => (
                  <option key={year} value={year}>{year}년</option>
                ))}
              </select>
              <span>~</span>
              <select 
                value={yearRange.end}
                onChange={(e) => setYearRange(prev => ({ ...prev, end: parseInt(e.target.value) }))}
              >
                {yearOptions.map(year => (
                  <option key={year} value={year}>{year}년</option>
                ))}
              </select>
            </div>
            <button 
              className="btn-primary"
              onClick={fetchStatsData}
              disabled={!canSearch || loading}
            >
              {loading ? '조회 중...' : '📊 통계 조회'}
            </button>
          </div>
        </div>
        
        {error && <div className="error-message">⚠️ {error}</div>}
      </section>

      {/* 차트 영역 */}
      {chartData && (
        <section className="chart-section">

          <ChartComponent data={chartData} analysisType="통계" />
        </section>
      )}

      {/* 데이터 테이블 */}
      <section className="data-table-section">
        <div className="table-header">
          <h3>📋 상세 데이터 ({statsData.length}건)</h3>
          <div className="download-buttons">
            <button className="btn-download" onClick={downloadCSV}>
              📄 CSV 다운로드
            </button>
            <button className="btn-download" onClick={downloadExcel}>
              📗 Excel 다운로드
            </button>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>년도</th>
                <th>월</th>
                <th>품목</th>
                <th>지역</th>
                <th>생산량(톤)</th>
                <th>판매량(톤)</th>
                <th>수입량(톤)</th>
                <th>전년 생산량(톤)</th>
                <th>전년 판매량(톤)</th>
                <th>전년 수입량(톤)</th>
                <th>생산 증감률(%)</th>
                <th>판매 증감률(%)</th>
                <th>수입 증감률(%)</th>
              </tr>
            </thead>
            <tbody>
              {statsData.length === 0 ? (
                <tr>
                  <td colSpan="13" className="no-data">
                    {loading ? '데이터를 불러오는 중...' : '조회 결과가 없습니다'}
                  </td>
                </tr>
              ) : (
                statsData.map((row, index) => (
                  <tr key={index}>
                    <td>{row.year}</td>
                    <td>{row.month}월</td>
                    <td>{row.item}</td>
                    <td>{row.location}</td>
                    <td>{formatNumber(row.production)}</td>
                    <td>{formatNumber(row.sales)}</td>
                    <td>{formatNumber(row.imports)}</td>
                    <td>{formatNumber(row.prevProduction)}</td>
                    <td>{formatNumber(row.prevSales)}</td>
                    <td>{formatNumber(row.prevImports)}</td>
                    <td className={getChangeClass(row.productionChange)}>
                      {formatPercent(row.productionChange)}
                    </td>
                    <td className={getChangeClass(row.salesChange)}>
                      {formatPercent(row.salesChange)}
                    </td>
                    <td className={getChangeClass(row.importsChange)}>
                      {formatPercent(row.importsChange)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 🔥 시계열 데이터 서버 연동 표시 */}
        <div className="data-source-info">
          <p><strong>📡 데이터 소스:</strong> 시계열 분석 모델에서 생성된 통계 데이터</p>
          <p><strong>🔄 업데이트:</strong> 매월 자동 갱신 (서버 DB 저장)</p>
        </div>
      </section>
    </div>
  )
}

// 모킹 데이터 생성 함수들
function generateMockStatsData() {
  const mockData = []
  const items = ['고등어', '갈치']
  const months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

  items.forEach(item => {
    months.forEach(month => {
      mockData.push({
        year: 2024,
        month,
        item,
        location: '부산',
        production: Math.floor(Math.random() * 1000) + 500,
        sales: Math.floor(Math.random() * 800) + 400,
        imports: Math.floor(Math.random() * 300) + 100,
        prevProduction: Math.floor(Math.random() * 900) + 450,
        prevSales: Math.floor(Math.random() * 750) + 350,
        prevImports: Math.floor(Math.random() * 250) + 80,
        productionChange: (Math.random() - 0.5) * 40,
        salesChange: (Math.random() - 0.5) * 30,
        importsChange: (Math.random() - 0.5) * 50
      })
    })
  })

  return mockData
}

var option = {
  scales: {
    xAxes: [{
      id: "bar-x-axis1",
      stacked: true,
      barThickness: 30,     
    }, {
      id: "bar-x-axis2",
      stacked: true,
      display: false,      
      barThickness: 10,
    }, {
      id: "bar-x-axis3",
      stacked: true,    
      barThickness: 30,
      display: false
    }],
  },
};

function processDataForChart(statsData) {
  // 데이터를 월별로 정렬
  console.log("로오오ㅗ그");
  const sortedData = [...statsData].sort((a, b) => {
    if (a.year !== b.year) return a.year - b.year;
    return a.month - b.month;
  });

  // X축 레이블과 각 데이터셋의 데이터를 추출
  const labels = sortedData.map(d => `${d.year}년 ${d.month}월`);
  const productionData = sortedData.map(d => d.production);
  const salesData = sortedData.map(d => d.sales);
  const importsData = sortedData.map(d => d.imports);

  return {
    labels: labels,
    datasets: [
      {
        label: '생산량',
        data: productionData,
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgb(255, 99, 132)',
        barPercentage: 0.8, // 가장 넓은 막대
        //stack: 'A', // 겹치기를 위한 스택 ID
      },
      {
        label: '판매량',
        data: salesData,
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        borderColor: 'rgb(54, 162, 235)',
        barPercentage: 0.5, // 중간 너비 막대
        //stack: 'A', // 겹치기를 위한 스택 ID
      },
      {
        label: '수입량',
        data: importsData,
        backgroundColor: 'rgba(75, 192, 192, 0.9)',
        borderColor: 'rgb(75, 192, 192)',
        barPercentage: 0.2, // 가장 좁은 막대
        //stack: 'A', // 겹치기를 위한 스택 ID
      }
    ],
    options : option
  };
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
  const headers = ['년도', '월', '품목', '지역', '생산량', '판매량', '수입량', '전년생산량', '전년판매량', '전년수입량', '생산증감률', '판매증감률', '수입증감률']
  const csvContent = [
    headers.join(','),
    ...data.map(row => [
      row.year, row.month, row.item, row.location,
      row.production, row.sales, row.imports,
      row.prevProduction, row.prevSales, row.prevImports,
      row.productionChange, row.salesChange, row.importsChange
    ].join(','))
  ].join('\n')
  
  return '\uFEFF' + csvContent // UTF-8 BOM 추가
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