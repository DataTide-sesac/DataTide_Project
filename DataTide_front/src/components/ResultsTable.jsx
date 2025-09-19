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
  selectedCategories, // Add selectedCategories prop
}) {
  // Define column configurations for '통계' analysis
  const statisticColumns = {
    '생산': {
      header: '생산량',
      prevHeader: '전년생산량',
      changeHeader: '생산증감률(%)',
      dataKey: 'production',
      prevDataKey: 'prevProduction',
      changeDataKey: 'productionChange',
    },
    '판매': {
      header: '판매량',
      prevHeader: '전년판매량',
      changeHeader: '판매증감률',
      dataKey: 'sales',
      prevDataKey: 'prevSales',
      changeDataKey: 'salesChange',
    },
    '수입': {
      header: '수입량(톤)',
      prevHeader: '전년수입량',
      changeHeader: '수입증감률',
      dataKey: 'inbound',
      prevDataKey: 'prevInbound',
      changeDataKey: 'inboundChange',
    },
  };

  // Determine which columns to display based on selectedCategories
  const getDisplayedColumns = () => {
    if (selectedAnalysis !== '통계' || !selectedCategories || selectedCategories.length === 0) {
      return [];
    }

    const columns = [];
    selectedCategories.forEach(category => {
      const colConfig = statisticColumns[category];
      if (colConfig) {
        columns.push(colConfig);
      }
    });
    return columns;
  };

  const displayedColumns = getDisplayedColumns();
  const colSpanValue = selectedAnalysis === '통계' ? (2 + (displayedColumns.length * 3)) : 7; // 2 for 년도, 품목 + (selected * 3)

  return (
    <section className="results-section">
      <div className="results-header">
        <h2>📋 상세 데이터 ({tableData.length}건)</h2>
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
                  {displayedColumns.map(col => (
                    <th key={`header-${col.dataKey}`}>{col.header}</th>
                  ))}
                  {displayedColumns.map(col => (
                    <th key={`prev-header-${col.prevDataKey}`}>{col.prevHeader}</th>
                  ))}
                  {displayedColumns.map(col => (
                    <th key={`change-header-${col.changeDataKey}`}>{col.changeHeader}</th>
                  ))}
                </>
              ) : (
                <>
                  <th>년월</th>
                  <th>품목</th>
                  <th>생산량(톤)</th>
                  <th>판매량(톤)</th>
                  <th>수입량(톤)</th>
                  <th>데이터구분</th>
                  {/* <th>신뢰도(%)</th> */}
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {tableData.length === 0 ? (
              <tr>
                <td colSpan={colSpanValue}>{loading ? '데이터를 불러오는 중...' : '품목과 동향을 선택하고 검색하세요'}</td>
              </tr>
            ) : (
              tableData.map((row, idx) => (
                <tr key={idx}>
                  <td>{row.period}</td>
                  <td>{selectedItem}</td>
                  {selectedAnalysis === '통계' ? (
                    <>
                      {displayedColumns.map(col => (
                        <td key={`data-${col.dataKey}`}>{formatNumber(row[col.dataKey])}</td>
                      ))}
                      {displayedColumns.map(col => (
                        <td key={`prev-data-${col.prevDataKey}`}>{formatNumber(row[col.prevDataKey])}</td>
                      ))}
                      {displayedColumns.map(col => (
                        <td key={`change-data-${col.changeDataKey}`}>{formatPercent(row[col.changeDataKey])}</td>
                      ))}
                    </>
                  ) : (
                    <>
                      <td>{formatNumber(row.production)}</td>
                      <td>{formatNumber(row.sales)}</td>
                      <td>{formatNumber(row.inbound)}</td>
                      <td>{row.dataType}</td>
                      {/* <td>{row.confidence ? `${row.confidence}%` : '-' }</td> */}
                    </>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="data-source-info">
        {/* <p><strong>데이터 소스:</strong> {selectedAnalysis === '통계' ? '과거 시계열 분석 모델' : 'LSTM 기반 AI 예측 모델'}</p>
        <p><strong>서버 API:</strong> {apiBaseUrl}/api/fisheries-analysis</p> */}
        <p><strong>업데이트 주기:</strong> 매월 1일 자동 갱신</p>
        {/* <p><strong>데이터 저장:</strong> MySQL 시계열 테이블에 저장 후 분석</p> */}
      </div>
    </section>
  );
}
