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
  const now = new Date();
  const pastX = [];
  const predictedX = [];

  // Generate past 6 months
  for (let i = 6; i > 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    pastX.push(`${d.getFullYear()}년 ${d.getMonth() + 1}월`);
  }

  // Generate future 6 months
  for (let i = 0; i < 6; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() + i, 1);
    predictedX.push(`${d.getFullYear()}년 ${d.getMonth() + 1}월`);
  }

  const predictionMockData = {
    '생산': { pastY: [10, 12, 15, 13, 16, 18], predictedY: [25, 27, 26, 28, 30, 29], color: '#5C6BC0', fill: 'rgba(92, 107, 192, 0.1)' },
    '판매': { pastY: [8, 10, 13, 11, 14, 16], predictedY: [23, 25, 24, 26, 28, 27], color: '#7CB342', fill: 'rgba(124, 179, 66, 0.1)' },
    '수입': { pastY: [5, 7, 9, 8, 10, 12], predictedY: [19, 21, 20, 22, 24, 23], color: '#FF8A65', fill: 'rgba(255, 138, 101, 0.1)' }
  };
  return { pastX, predictedX, predictionMockData };
}

export function generateBumpChartData(){
  const now = new Date();

  // x축(시간)
  const months = [];
  for (let i = 6; i > 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push(`${d.getFullYear()}년 ${d.getMonth() + 1}월`);
  }

  // 데이터 예시: 고등어, 오징어, 갈치 3개 품목
  const predictionMockData = {
    '고등어': [1, 3, 2, 2, 3, 2],
    '오징어': [2, 1, 3, 3, 1, 1],
    '갈치': [3, 2, 1, 1, 2, 3],
  };


  // nivo/bump에 맞게 변환
  const data = Object.entries(predictionMockData).map(([key, values]) => ({
    id: key,
    data: months.map((month, idx) => ({
      x: month,
      y: values[idx]
    }))
  }));

  return data;
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

    // Prepend previous month's data to connect the line graph
    if (startMonth > 1) {
      const prevMonthLabel = allMonths[startMonth - 2];
      monthLabels.unshift(prevMonthLabel);

      ['생산', '판매', '수입'].forEach(cat => {
        const prevMonthData = fullYData.previous[cat][startMonth - 2];
        yData.current[cat].unshift(prevMonthData);
        yData.previous[cat].unshift(null); // Add null to bar data to keep it aligned
      });
    }

    const datasets = [
      { type: 'line', order: 2, label: `${startYear === endYear ? endYear : `${startYear}~${endYear}`} 생산`, data: yData.current['생산'], borderColor: '#1565C0' },
      { type: 'line', order: 2, label: `${startYear === endYear ? endYear : `${startYear}~${endYear}`} 판매`, data: yData.current['판매'], borderColor: '#388E3C' },
      { type: 'line', order: 2, label: `${startYear === endYear ? endYear : `${startYear}~${endYear}`} 수입`, data: yData.current['수입'], borderColor: '#F57C00' },
      { type: 'bar', order: 1, label: `${startYear === endYear ? endYear - 1 : `${startYear - 1}~${endYear - 1}`} 생산`, data: yData.previous['생산'], backgroundColor: 'rgba(100, 181, 246, 1)' },
      { type: 'bar', order: 1, label: `${startYear === endYear ? endYear - 1 : `${startYear - 1}~${endYear - 1}`} 판매`, data: yData.previous['판매'], backgroundColor: 'rgba(129, 199, 132, 1)' },
      { type: 'bar', order: 1, label: `${startYear === endYear ? endYear - 1 : `${startYear - 1}~${endYear - 1}`} 수입`, data: yData.previous['수입'], backgroundColor: 'rgba(255, 183, 77, 1)' },
    ];
    
    const filteredDatasets = datasets.filter(dataset => {
      const category = dataset.label.split(' ').pop();
      return selectedCategories.includes(category);
    });

    return {
      labels: monthLabels,
      datasets: filteredDatasets,
    };
  }

  // For prediction chart, keep original Plotly data structure
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