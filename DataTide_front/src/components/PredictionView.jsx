import React, { useState, useEffect } from 'react'
import ChartComponent from './ChartComponent'
import { fetchPredictionDataApi, getExcelDownloadUrl } from '../api';
import * as XLSX from 'xlsx';

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


    } catch (err) {
      setError(err.message || '예측 데이터를 가져오는 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }



  function handleDownloadCSV() {
        const headers = [];
        // 현재 테이블에 보이는 헤더를 동적으로 생성
        const headerElements = document.querySelectorAll('.data-table thead th');
        headerElements.forEach(th => headers.push(`"${th.textContent}"`));
  
        const rows = [];
        // 현재 테이블에 보이는 데이터를 동적으로 생성
        const rowElements = document.querySelectorAll('.data-table tbody tr');
        rowElements.forEach(tr => {
          const rowData = [];
          tr.querySelectorAll('td').forEach(td => {
            // 쉼표가 포함된 숫자를 처리하기 위해 큰따옴표로 감싸기
            rowData.push(`"${td.textContent}"`);
          });
          rows.push(rowData.join(','));
        });
  
        const csvContent = [headers.join(','), ...rows].join('\r\n');
  
        // 파일 다운로드 실행
        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8-sig;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Fish_data.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
  
      function handleDownloadXLSX() {
        // 1) 테이블 헤더 가져오기
        const headers = [];
        document.querySelectorAll('.data-table thead th').forEach(th => {
          headers.push(th.textContent.trim());
        });
  
        // 2) 테이블 바디 데이터 가져오기
        const data = [];
        document.querySelectorAll('.data-table tbody tr').forEach(tr => {
          const row = [];
          tr.querySelectorAll('td').forEach(td => {
            row.push(td.textContent.trim());
          });
          data.push(row);
        });
  
        // 3) 헤더 + 데이터 합치기
        const worksheetData = [headers, ...data];
  
        // 4) 워크시트 생성
        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
  
        // 5) 워크북 생성 및 워크시트 추가
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet1');
  
        // 6) 파일 저장 (xlsx 확장자)
        XLSX.writeFile(workbook, 'Fish_data.xlsx');
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
            <button className="btn-download" onClick={handleDownloadCSV}>
              📄 CSV 다운로드
            </button>
            <button className="btn-download" onClick={handleDownloadXLSX}>
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
                <th>생산량(톤)</th>
                <th>수입량(톤)</th>
                <th>판매량(톤)</th>
                <th>데이터 타입</th>
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
                    <td>{formatNumber(row.imports)}</td>
                    <td>{formatNumber(row.sales)}</td>
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

// 유틸리티 함수들 (동일)
function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return new Intl.NumberFormat('ko-KR').format(value)
}