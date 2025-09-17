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

export function generateBumpChartData(result, period, allItems = null) {
    // 1. 데이터 유효성 검사
    if (!result || !result.chartData || !result.categories || result.chartData.length === 0) {
      return null;
    }

    if (!allItems) {
      allItems = result.categories;
    }

    // 2. 기준 라벨 생성 ('YYYY-MM' 형식)
    const labels = [];
    let year = period.startYear;
    let month = period.startMonth;
    while (year < period.endYear || (year === period.endYear && month <= period.endMonth)) {
      labels.push(year + '-' + month.toString().padStart(2, '0'));
      month++;
      if (month > 12) {
        month = 1;
        year++;
      }
    }

    // 3. '생산' 데이터만 필터링
    const productionData = result.chartData.filter(trace => trace.name.includes('(생산)'));

    // 4. 월별/품목별 생산량 데이터 가공
    const monthData = labels.map(monthLabel => {
      const monthEntry = {};
      allItems.forEach(item => {
        const trace = productionData.find(trace => trace.name.includes(item));
        if (trace && Array.isArray(trace.x)) {
          const idx = trace.x.indexOf(monthLabel);
          monthEntry[item] = idx >= 0 ? trace.y[idx] || 0 : 0;
        } else {
          monthEntry[item] = 0;
        }
      });
      return monthEntry;
    });

    // 5. 월별 순위 계산
    const ranksByMonth = monthData.map(monthEntry => {
      const entries = Object.entries(monthEntry);
      entries.sort((a, b) => b[1] - a[1]);
      const rankMap = {};
      entries.forEach(([item], idx) => {
        rankMap[item] = idx + 1;
      });
      return rankMap;
    });

    // 6. 최종 bumpData 생성 (라벨 생성 로직 수정)
    const bumpData = allItems.map(item => ({
      id: item,
      data: labels.map((monthLabel, idx) => {
        const parts = monthLabel.split('-');
        const currentYear = parts[0];
        const currentMonth = parts[1];

        let displayLabel;

        // 첫 번째 라벨이거나, 이전 라벨과 연도가 다를 경우 'YYYY년 MM월'
        if (idx === 0 || currentYear !== labels[idx - 1].split('-')[0]) {
          displayLabel = currentYear + '년 ' + currentMonth + '월';
        } else {
          // 그 외에는 'MM월'
          displayLabel = currentMonth + '월';
        }

        return {
          x: displayLabel,
          y: ranksByMonth[idx][item] || allItems.length,
        };
      }),
    }));

    return bumpData;
  }





//// 산포도 차트
export function generateScatterChartData(){
  const now = new Date();

  // x축(시간)
  const months = [];
  for (let i = 6; i > 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push(`${d.getFullYear()}년 ${d.getMonth() + 1}월`);
  }

  // 데이터 예시: 고등어, 오징어, 갈치 3개 품목
  // const predictionMockData = {
  //   '고등어': [1, 3, 2, 2, 3, 2],
  //   '오징어': [2, 1, 3, 3, 1, 1],
  //   '갈치': [3, 2, 1, 1, 2, 3],
  // };

  const predictionMockData =
    [
      {
        id : '고등어',
        data:[
          {x : 0, y: 1},
          {x : 1, y: 4},
          {x : 2, y: 5},
          {x : 3, y: 6},
          {x : 4, y: 2},
          {x : 5, y: 3},
        ]
      },
      {
        id : '오징어',
        data:[
          {x : 0, y: 4},
          {x : 1, y: 5},
          {x : 2, y: 7},
          {x : 3, y: 2},
          {x : 4, y: 3},
          {x : 5, y: 1},
        ]
      },
      {
        id : '갈치',
        data:[
          {x : 0, y: 6},
          {x : 1, y: 2},
          {x : 2, y: 1},
          {x : 3, y: 9},
          {x : 4, y: 6},
          {x : 5, y: 2},
        ]
      }
    ]

  return predictionMockData;
}
////

//// 버블 차트
export function generateBubbleChartData(){
  const now = new Date();

  // x축(시간)
  const months = [];
  for (let i = 6; i > 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push(`${d.getFullYear()}년 ${d.getMonth() + 1}월`);
  }


  const predictionMockData =
    [
      {
        id : '고등어',
        data:[
          {x : 1, y: 1, size: 30},
          {x : 2, y: 4, size: 10},
          {x : 3, y: 5, size: 80},
          {x : 4, y: 6, size: 20},
          {x : 5, y: 2, size: 60},
          {x : 6, y: 3, size: 40},
          {x : 7, y: 6, size: 35},
          {x : 8, y: 2, size: 33},
          {x : 9, y: 1, size: 50},
          {x : 10, y: 9, size: 20},
          {x : 11, y: 6, size: 27},
          {x : 12, y: 2, size: 16}
        ]
      },
      {
        id : '오징어',
        data:[
          {x : 1, y: 4, size: 15},
          {x : 2, y: 5, size: 30},
          {x : 3, y: 7, size: 20},
          {x : 4, y: 2, size: 10},
          {x : 5, y: 3, size: 40},
          {x : 6, y: 1, size: 47},
          {x : 7, y: 1, size: 30},
          {x : 8, y: 4, size: 10},
          {x : 9, y: 5, size: 80},
          {x : 10, y: 6, size: 20},
          {x : 11, y: 2, size: 60},
          {x : 12, y: 3, size: 40}
          
        ]
      },
      {
        id : '갈치',
        data:[
          {x : 1, y: 6, size: 35},
          {x : 2, y: 2, size: 33},
          {x : 3, y: 1, size: 50},
          {x : 4, y: 0, size: 20},
          {x : 5, y: 6, size: 27},
          {x : 6, y: 2, size: 16},
          {x : 7, y: 4, size: 15},
          {x : 8, y: 5, size: 30},
          {x : 9, y: 7, size: 20},
          {x : 10, y: 2, size: 10},
          {x : 11, y: 3, size: 40},
          {x : 12, y: 1, size: 47}
        ]
      }
    ]

  return predictionMockData;
}
////

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

export function isValidChartData(data) {
  return (
    data &&
    typeof data === 'object' &&
    Array.isArray(data.datasets) &&
    data.datasets.length > 0
  );
}