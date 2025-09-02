import React from 'react';
import { formatNumber, formatPercent } from '../utils';

export default function ResultsTable({
  tableData,
  loading,
  selectedItem,
  selectedAnalysis,
  downloadCSV,
  downloadExcel,
  apiBaseUrl,
  yearRange,
}) {
  return (
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

      <div className="data-source-info">
        <p><strong>데이터 소스:</strong> {selectedAnalysis === '통계' ? '과거 시계열 분석 모델' : 'LSTM 기반 AI 예측 모델'}</p>
        <p><strong>서버 API:</strong> {apiBaseUrl}/api/fisheries-analysis</p>
        <p><strong>업데이트 주기:</strong> 매월 1일 자동 갱신</p>
        <p><strong>데이터 저장:</strong> MySQL 시계열 테이블에 저장 후 분석</p>
      </div>
    </section>
  );
}
