export function generateMockData() {
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

function generatePredictionChartData() {
  const pastX = ['2023년 01월', '2023년 02월', '2023년 03월', '2023년 04월', '2023년 05월', '2023년 06월', '2023년 07월', '2023년 08월', '2023년 09월', '2023년 10월', '2023년 11월', '2023년 12월'];
  const predictedX = ['2024년 01월', '2024년 02월', '2024년 03월', '2024년 04월', '2024년 05월', '2024년 06월', '2024년 07월', '2024년 08월', '2024년 09월', '2024년 10월', '2024년 11월', '2024년 12월'];
  const predictionMockData = {
    '생산': { pastY: [10, 12, 15, 13, 16, 18, 20, 19, 22, 21, 24, 23], predictedY: [25, 27, 26, 28, 30, 29, 32, 31, 33, 35, 34, 36], color: '#5C6BC0', fill: 'rgba(92, 107, 192, 0.1)' },
    '판매': { pastY: [8, 10, 13, 11, 14, 16, 18, 17, 20, 19, 22, 21], predictedY: [23, 25, 24, 26, 28, 27, 30, 29, 31, 33, 32, 34], color: '#7CB342', fill: 'rgba(124, 179, 66, 0.1)' },
    '수입': { pastY: [5, 7, 9, 8, 10, 12, 14, 13, 16, 15, 18, 17], predictedY: [19, 21, 20, 22, 24, 23, 26, 25, 27, 29, 28, 30], color: '#FF8A65', fill: 'rgba(255, 138, 101, 0.1)' }
  };
  return { pastX, predictedX, predictionMockData };
}

export function generateMockChartData({ analysisType, period, selectedCategories }) {
  if (analysisType === '통계') {
    const { startYear, endYear, startMonth, endMonth } = period;
    const allMonths = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    
    const fullYData = {
      current: {
        '생산': [25, 18, 27, 38, 33, 49, 36, 40, 43, 37, 44, 47],
        '판매': [21, 16, 25, 33, 28 , 43, 32, 35, 38, 31, 39, 41],
        '수입': [18, 13, 22, 27, 24, 38, 29, 33, 35, 28, 36, 39]
      },
      previous: {
        '생산': [18, 12, 20, 30, 25, 40, 28, 32, 35, 28, 35, 38],
        '판매': [15, 10, 18, 25, 20, 35, 25, 28, 30, 25, 30, 33],
        '수입': [12, 8, 15, 20, 18, 30, 22, 25, 28, 22, 28, 30]
      }
    };

    let monthLabels = [];
    const yData = { current: {}, previous: {} };
    ['생산', '판매', '수입'].forEach(cat => {
        yData.current[cat] = [];
        yData.previous[cat] = [];
    });

    if (startYear === endYear) {
        monthLabels = allMonths.slice(startMonth - 1, endMonth);
        ['생산', '판매', '수입'].forEach(cat => {
            yData.current[cat] = fullYData.current[cat].slice(startMonth - 1, endMonth);
            yData.previous[cat] = fullYData.previous[cat].slice(startMonth - 1, endMonth);
        });
    } else { 
        monthLabels.push(...allMonths.slice(startMonth - 1));
        ['생산', '판매', '수입'].forEach(cat => {
            yData.current[cat].push(...fullYData.current[cat].slice(startMonth - 1));
            yData.previous[cat].push(...fullYData.previous[cat].slice(startMonth - 1));
        });
        monthLabels.push(...allMonths.slice(0, endMonth));
        ['생산', '판매', '수입'].forEach(cat => {
            yData.current[cat].push(...fullYData.current[cat].slice(0, endMonth));
            yData.previous[cat].push(...fullYData.previous[cat].slice(0, endMonth));
        });
    }

    const traces = [
      { x: monthLabels, y: yData.current['생산'], name: `${startYear === endYear ? endYear : `${startYear}~${endYear}`} 생산`, type: 'scatter', mode: 'lines+markers', marker: { color: '#1565C0' } },
      { x: monthLabels, y: yData.current['판매'], name: `${startYear === endYear ? endYear : `${startYear}~${endYear}`} 판매`, type: 'scatter', mode: 'lines+markers', marker: { color: '#388E3C' } },
      { x: monthLabels, y: yData.current['수입'], name: `${startYear === endYear ? endYear : `${startYear}~${endYear}`} 수입`, type: 'scatter', mode: 'lines+markers', marker: { color: '#F57C00' } },
      { x: monthLabels, y: yData.previous['생산'], name: `${startYear === endYear ? endYear - 1 : `${startYear - 1}~${endYear - 1}`} 생산`, type: 'bar', marker: { color: 'rgba(100, 181, 246, 0.6)' } },
      { x: monthLabels, y: yData.previous['판매'], name: `${startYear === endYear ? endYear - 1 : `${startYear - 1}~${endYear - 1}`} 판매`, type: 'bar', marker: { color: 'rgba(129, 199, 132, 0.60)' } },
      { x: monthLabels, y: yData.previous['수입'], name: `${startYear === endYear ? endYear - 1 : `${startYear - 1}~${endYear - 1}`} 수입`, type: 'bar', marker: { color: 'rgba(255, 183, 77, 0.60)' } },
    ];

    const filteredTraces = traces.filter(trace => selectedCategories.some(category => trace.name.includes(category)));
    return filteredTraces;
  }

  if (analysisType === '예측') {
    const { pastX, predictedX, predictionMockData } = generatePredictionChartData();
    const predictionData = [];
    selectedCategories.forEach(category => {
      const categoryData = predictionMockData[category];
      if (categoryData) {
        const { pastY, predictedY, color, fill } = categoryData;
        const pastXConnected = [...pastX, predictedX[0]];
        const pastYConnected = [...pastY, predictedY[0]];
        predictionData.push({ x: pastXConnected, y: pastYConnected, name: `과거 데이터 ${category}`, type: 'scatter', mode: 'lines', line: { color: color } });
        predictionData.push({ x: predictedX, y: predictedY, name: `예측 데이터 ${category}`, type: 'scatter', mode: 'lines', line: { color: color, dash: 'dash' } });
        predictionData.push({ x: [...predictedX, ...[...predictedX].reverse()], y: [...predictedY.map(y => y - 2), ...[...predictedY].reverse().map(y => y + 2)], fill: 'toself', fillcolor: fill, line: { color: 'transparent' }, name: `신뢰구간 ${category}`, showlegend: false, type: 'scatter' });
      }
    });
    return predictionData;
  }

  return [];
}

export function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  return new Intl.NumberFormat('ko-KR').format(value)
}

export function formatPercent(value) {
  if (value === null || value === undefined || isNaN(value)) return '-'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}

export function getChangeClass(value) {
  if (value > 0) return 'positive-change'
  if (value < 0) return 'negative-change'
  return ''
}

export function convertToCSV(data) {
  const headers = ['기간', '생산량', '판매량', '수입량']
  const csvContent = [
    headers.join(','),
    ...data.map(row => [
      row.period, row.production, row.sales, row.imports
    ].join(','))
  ].join('')
  
  return '\uFEFF' + csvContent
}

export function downloadFile(content, fileName, contentType) {
  const blob = new Blob([content], { type: contentType })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  window.URL.revokeObjectURL(url)
}