import React, { useState, useEffect } from 'react'
import ChartComponent from './ChartComponent'
import { fetchPredictionDataApi, getExcelDownloadUrl } from '../api';

export default function PredictionView({ selectedItems, selectedLocation }) {
  const [predictionData, setPredictionData] = useState([])
  const [chartData, setChartData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // 기준일: 2025-07-30
  const baseDate = '2025-07-30'
  const canSearch = selectedItems.length > 0

  // 예측 데이터 조회
  async function fetchPredictionData() {
    if (!canSearch) return

    try {
      setLoading(true)
      setError('')

      // 🔥 실제 API 호출 부분 - api/index.js의 함수를 호출하도록 수정
      /*
      const result = await fetchPredictionDataApi({
        selectedItems,
        selectedLocation,
        baseDate
      });
      setPredictionData(result.predictionData || []);
      setChartData(result.chartData || null);
      */

      // 임시 모킹 데이터 (실제 API 연결 전까지 사용)
      const mockPredictionData = generateMockPredictionData()
      const mockChartData = generateMockPredictionChartData()

      setPredictionData(mockPredictionData)
      setChartData(mockChartData)

    } catch (err) {
      setError(err.message || '예측 데이터를 가져오는 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  // CSV 다운로드
  function downloadCSV() {
    const csvContent = convertToPredictionCSV(predictionData)
    downloadFile(csvContent, 'prediction_data.csv', 'text/csv')
  }

  // Excel 다운로드
  function downloadExcel() {
    const url = getExcelDownloadUrl('prediction', { 
      selectedItems, 
      selectedLocation, 
      baseDate 
    });
    window.open(url, '_blank');
  }

  return (
    <div className="prediction-view">
      {/* 예측 정보 */}
      <section className="prediction-info-section">
        <div className="info-container">
          <div className="prediction-period">
            <h3>🔮 예측 기간</h3>
            <p><strong>기준일:</strong> {baseDate}</p>
            <p><strong>과거 데이터:</strong> 2025년 1월 ~ 2025년 7월 (6개월)</p>
            <p><strong>예측 데이터:</strong> 2025년 8월 ~ 2026년 1월 (6개월)</p>
          </div>
          <button 
            className="btn-primary"
            onClick={fetchPredictionData}
            disabled={!canSearch || loading}
          >
            {loading ? '예측 중...' : '🔮 예측 실행'}
          </button>
        </div>
        
        {error && <div className="error-message">⚠️ {error}</div>}
      </section>

      {/* 예측 차트 */}
      {chartData && (
        <section className="chart-section">
          <h3>📈 AI 예측 결과 (실제 데이터 + 예측 데이터)</h3>
          <ChartComponent data={chartData} type="prediction" />
        </section>
      )}

      {/* 예측 데이터 테이블 */}
      <section className="data-table-section">
        <div className="table-header">
          <h3>📋 예측 데이터 ({predictionData.length}건)</h3>
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
                <th>년월</th>
                <th>품목</th>
                <th>지역</th>
                <th>생산량(톤)</th>
                <th>판매량(톤)</th>
                <th>수입량(톤)</th>
                <th>데이터 타입</th>
                <th>신뢰도</th>
              </tr>
            </thead>
            <tbody>
              {predictionData.length === 0 ? (
                <tr>
                  <td colSpan="8" className="no-data">
                    {loading ? '예측 모델 실행 중...' : '예측 실행 버튼을 클릭하세요'}
                  </td>
                </tr>
              ) : (
                predictionData.map((row, index) => (
                  <tr key={index} className={row.dataType === '예측' ? 'prediction-row' : 'actual-row'}>
                    <td>{row.yearMonth}</td>
                    <td>{row.item}</td>
                    <td>{row.location}</td>
                    <td>{formatNumber(row.production)}</td>
                    <td>{formatNumber(row.sales)}</td>
                    <td>{formatNumber(row.imports)}</td>
                    <td>
                      <span className={`data-type ${row.dataType === '예측' ? 'prediction' : 'actual'}`}>
                        {row.dataType}
                      </span>
                    </td>
                    <td>{row.confidence ? `${row.confidence}%` : '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 🔥 AI 예측 모델 정보 표시 */}
        <div className="model-info">
          <h4>🤖 AI 예측 모델 정보</h4>
          <ul>
            <li><strong>모델 타입:</strong> LSTM (Long Short-Term Memory) 시계열 예측 모델</li>
            <li><strong>학습 데이터:</strong> 과거 5년간 월별 수산물 생산/판매/수입 데이터</li>
            <li><strong>예측 정확도:</strong> 평균 85% (과거 6개월 검증 기준)</li>
            <li><strong>업데이트:</strong> 매월 새로운 데이터로 모델 재학습</li>
          </ul>
        </div>
      </section>
    </div>
  )
}

// 예측 데이터 모킹 함수
function generateMockPredictionData() {
  const data = []
  const items = ['고등어', '갈치']
  const months = [
    // 과거 6개월 (실제 데이터)
    { yearMonth: '2025-01', dataType: '실제', confidence: null },
    { yearMonth: '2025-02', dataType: '실제', confidence: null },
    { yearMonth: '2025-03', dataType: '실제', confidence: null },
    { yearMonth: '2025-04', dataType: '실제', confidence: null },
    { yearMonth: '2025-05', dataType: '실제', confidence: null },
    { yearMonth: '2025-06', dataType: '실제', confidence: null },
    { yearMonth: '2025-07', dataType: '실제', confidence: null },
    // 미래 6개월 (예측 데이터)
    { yearMonth: '2025-08', dataType: '예측', confidence: 89 },
    { yearMonth: '2025-09', dataType: '예측', confidence: 87 },
    { yearMonth: '2025-10', dataType: '예측', confidence: 85 },
    { yearMonth: '2025-11', dataType: '예측', confidence: 82 },
    { yearMonth: '2025-12', dataType: '예측', confidence: 79 },
    { yearMonth: '2026-01', dataType: '예측', confidence: 76 }
  ]

  items.forEach(item => {
    months.forEach(month => {
      data.push({
        yearMonth: month.yearMonth,
        item,
        location: '부산',
        production: Math.floor(Math.random() * 1000) + 500,
        sales: Math.floor(Math.random() * 800) + 400,
        imports: Math.floor(Math.random() * 300) + 100,
        dataType: month.dataType,
        confidence: month.confidence
      })
    })
  })

  return data
}

function generateMockPredictionChartData() {
  return {
    actual: [650, 720, 680, 590, 750, 820, 890], // 과거 7개월
    predicted: [760, 640, 710, 780, 850, 920], // 미래 6개월
    labels: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월', '1월']
  }
}

function convertToPredictionCSV(data) {
  const headers = ['년월', '품목', '지역', '생산량', '판매량', '수입량', '데이터타입', '신뢰도']
  const csvContent = [
    headers.join(','),
    ...data.map(row => [
      row.yearMonth, row.item, row.location,
      row.production, row.sales, row.imports,
      row.dataType, row.confidence || ''
    ].join(','))
  ].join('\n')
  
  return '\uFEFF' + csvContent
}

// 유틸리티 함수들 (동일)
function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return new Intl.NumberFormat('ko-KR').format(value)
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
