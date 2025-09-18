import React from 'react';
import { formatNumber, formatPercent } from '../utils';
import * as XLSX from 'xlsx';

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
    <section className="results-section">
      <div className="results-header">
        <h2>📋 상세 데이터 ({tableData.length}건)</h2>
        <div className="download-buttons">
          <button className="download-btn" onClick={handleDownloadCSV}>
            📄 CSV 다운로드
          </button>
          <button className="download-btn" onClick={handleDownloadXLSX}>
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
                  <th>수입량(톤)</th>
                  <th>판매량(톤)</th>
                  <th>데이터구분</th>
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
                      <td>{formatNumber(row.inbound)}</td>
                      <td>{formatNumber(row.sales)}</td>
                      <td>{row.dataType}</td>
                    </>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="data-source-info">
        <p><strong>업데이트 주기:</strong> 매월 1일 자동 갱신</p>
      </div>
    </section>
  );
}