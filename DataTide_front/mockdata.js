// // 이 함수를 DashboardPage 내로 이동 또는 utils.js에 정의할 수 있습니다.
// const generateDynamicChartData = (period, categories) => {
//   const { startYear, endYear, startMonth, endMonth } = period;
//   const allMonths = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
  
//   const fullYData = {
//     current: {
//       '생산': [25, 18, 27, 38, 33, 49, 36, 40, 43, 37, 44, 47],
//       '판매': [21, 16, 25, 33, 28, 43, 32, 35, 38, 31, 39, 41],
//       '수입': [18, 13, 22, 27, 24, 38, 29, 33, 35, 28, 36, 39]
//     },
//     previous: {
//       '생산': [18, 12, 20, 30, 25, 40, 28, 32, 35, 28, 35, 38],
//       '판매': [15, 10, 18, 25, 20, 35, 25, 28, 30, 25, 30, 33],
//       '수입': [12, 8, 15, 20, 18, 30, 22, 25, 28, 22, 28, 30]
//     }
//   };

//   let monthLabels = allMonths;
//   let yData = fullYData;

//   // 사용자가 선택한 기간에 맞춰 데이터 슬라이싱
//   if (startYear === endYear && startMonth >= 1 && endMonth <= 12 && startMonth <= endMonth) {
//     monthLabels = allMonths.slice(startMonth - 1, endMonth);
//     const sliceData = (data) => data.slice(startMonth - 1, endMonth);
//     yData = {
//       current: {
//         '생산': sliceData(fullYData.current['생산']),
//         '판매': sliceData(fullYData.current['판매']),
//         '수입': sliceData(fullYData.current['수입']),
//       },
//       previous: {
//         '생산': sliceData(fullYData.previous['생산']),
//         '판매': sliceData(fullYData.previous['판매']),
//         '수입': sliceData(fullYData.previous['수입']),
//       }
//     };
//   }

//   const traces = [
//     {
//       x: monthLabels,
//       y: yData.current['생산'],
//       name: `${endYear}(생산)`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#1565C0' },
//     },
//     {
//       x: monthLabels,
//       y: yData.current['판매'],
//       name: `${endYear}(판매)`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#388E3C' },
//     },
//     {
//       x: monthLabels,
//       y: yData.current['수입'],
//       name: `${endYear}(수입)`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#F57C00' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['생산'],
//       name: `${endYear - 1}(생산)`,
//       type: 'bar',
//       marker: { color: 'rgba(100, 181, 246, 0.65)' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['판매'],
//       name: `${endYear - 1}(판매)`,
//       type: 'bar',
//       marker: { color: 'rgba(129, 199, 132, 0.65)' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['수입'],
//       name: `${endYear - 1}(수입)`,
//       type: 'bar',
//       marker: { color: 'rgba(255, 183, 77, 0.65)' },
//     },
//   ];

//   // 선택된 카테고리에 따라 필터링
//   return traces.filter(trace => {
//     const categoryMatch = trace.name.match(/\(([^)]+)\)/);
//     return categoryMatch && categories.includes(categoryMatch[1].trim());
//   });
// };



//   // Mock data for prediction chart
//   const pastX = ['2023년 01월', '2023년 02월', '2023년 03월', '2023년 04월', '2023년 05월', '2023년 06월', '2023년 07월', '2023년 08월', '2023년 09월', '2023년 10월', '2023년 11월', '2023년 12월'];
//   const predictedX = ['2024년 01월', '2024년 02월', '2024년 03월', '2024년 04월', '2024년 05월', '2024년 06월', '2024년 07월', '2024년 08월', '2024년 09월', '2024년 10월', '2024년 11월', '2024년 12월'];

//   const predictionMockData = {
//     '생산': {
//       pastY: [10, 12, 15, 13, 16, 18, 20, 19, 22, 21, 24, 23],
//       predictedY: [25, 27, 26, 28, 30, 29, 32, 31, 33, 35, 34, 36],
//       color: '#5C6BC0',
//       fill: 'rgba(92, 107, 192, 0.1)'
//     },
//     '판매': {
//       pastY: [8, 10, 13, 11, 14, 16, 18, 17, 20, 19, 22, 21],
//       predictedY: [23, 25, 24, 26, 28, 27, 30, 29, 31, 33, 32, 34],
//       color: '#7CB342',
//       fill: 'rgba(124, 179, 66, 0.1)'
//     },
//     '수입': {
//       pastY: [5, 7, 9, 8, 10, 12, 14, 13, 16, 15, 18, 17],
//       predictedY: [19, 21, 20, 22, 24, 23, 26, 25, 27, 29, 28, 30],
//       color: '#FF8A65',
//       fill: 'rgba(255, 138, 101, 0.1)'
//     }
//   };

//   const predictionData = [];
//   selectedCategories.forEach(category => {
//     const trimmedCategory = category.trim();
//     const categoryData = predictionMockData[trimmedCategory];
//     if (categoryData) {
//       const { pastY, predictedY, color, fill } = categoryData;
//       const pastXConnected = [...pastX, predictedX[0]];
//       const pastYConnected = [...pastY, predictedY[0]];

//       predictionData.push({
//         x: pastXConnected,
//         y: pastYConnected,
//         name: `과거 데이터(${category})`,
//         type: 'scatter',
//         mode: 'lines',
//         line: { color: color },
//       });
//       predictionData.push({
//         x: predictedX,
//         y: predictedY,
//         name: `예측 데이터(${category})`,
//         type: 'scatter',
//         mode: 'lines',
//         line: { color: color, dash: 'dash' },
//       });
//       predictionData.push({
//         x: [...predictedX, ...[...predictedX].reverse()],
//         y: [...predictedY.map(y => y - 2), ...[...predictedY].reverse().map(y => y + 2)],
//         fill: 'toself',
//         fillcolor: fill,
//         line: { color: 'transparent' },
//         name: `신뢰구간(${category})`,
//         showlegend: false,
//         type: 'scatter',
//       });
//     }
//   });


//   const allX = [...pastX, ...predictedX];
//   const ticktext = allX.map((label, index) => {
//     const [year, month] = label.split(' ');

//     if (index === 0) {
//       return label;
//     }

//     const [prevYear] = allX[index - 1].split(' ');
//     if (year !== prevYear) {
//       return label;
//     }

//     return month;
//   });

// tickvals: allX,
//       ticktext: ticktext,


// 이 함수를 DashboardPage 내로 이동 또는 utils.js에 정의할 수 있습니다.
// const generateDynamicChartData = (period, categories) => {
//   const { startYear, endYear, startMonth, endMonth } = period;
//   const allMonths = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
  
//   const fullYData = {
//     current: {
//       '생산': [25, 18, 27, 38, 33, 49, 36, 40, 43, 37, 44, 47],
//       '판매': [21, 16, 25, 33, 28, 43, 32, 35, 38, 31, 39, 41],
//       '수입': [18, 13, 22, 27, 24, 38, 29, 33, 35, 28, 36, 39]
//     },
//     previous: {
//       '생산': [18, 12, 20, 30, 25, 40, 28, 32, 35, 28, 35, 38],
//       '판매': [15, 10, 18, 25, 20, 35, 25, 28, 30, 25, 30, 33],
//       '수입': [12, 8, 15, 20, 18, 30, 22, 25, 28, 22, 28, 30]
//     }
//   };

//   let monthLabels = allMonths;
//   let yData = fullYData;

//   // 사용자가 선택한 기간에 맞춰 데이터 슬라이싱
//   if (startYear === endYear && startMonth >= 1 && endMonth <= 12 && startMonth <= endMonth) {
//     monthLabels = allMonths.slice(startMonth - 1, endMonth);
//     const sliceData = (data) => data.slice(startMonth - 1, endMonth);
//     yData = {
//       current: {
//         '생산': sliceData(fullYData.current['생산']),
//         '판매': sliceData(fullYData.current['판매']),
//         '수입': sliceData(fullYData.current['수입']),
//       },
//       previous: {
//         '생산': sliceData(fullYData.previous['생산']),
//         '판매': sliceData(fullYData.previous['판매']),
//         '수입': sliceData(fullYData.previous['수입']),
//       }
//     };
//   }

//   const traces = [
//     {
//       x: monthLabels,
//       y: yData.current['생산'],
//       name: `${endYear} 생산`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#1565C0' },
//     },
//     {
//       x: monthLabels,
//       y: yData.current['판매'],
//       name: `${endYear} 판매`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#388E3C' },
//     },
//     {
//       x: monthLabels,
//       y: yData.current['수입'],
//       name: `${endYear} 수입`,
//       type: 'scatter',
//       mode: 'lines+markers',
//       marker: { color: '#F57C00' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['생산'],
//       name: `${endYear - 1} 생산`,
//       type: 'bar',
//       marker: { color: 'rgba(100, 181, 246, 0.65)' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['판매'],
//       name: `${endYear - 1} 판매`,
//       type: 'bar',
//       marker: { color: 'rgba(129, 199, 132, 0.65)' },
//     },
//     {
//       x: monthLabels,
//       y: yData.previous['수입'],
//       name: `${endYear - 1} 수입`,
//       type: 'bar',
//       marker: { color: 'rgba(255, 183, 77, 0.65)' },
//     },
//   ];

//   // 선택된 카테고리에 따라 필터링 (괄호 없이 이름에 포함되는지로 확인) 위에 코드와 거의 똑같지만, 이 문단이 다름
//   return traces.filter(trace => {
//     return categories.some(category => trace.name.includes(category));
//   });
// };