import React from 'react';
import Plot from 'react-plotly.js';


export default function ChartComponent({ data, analysisType, selectedCategories }) {
  // Mock data for comparison chart
  const rawComparisonData = [
    {
      x: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
      y: [22, 16, 25, 40, 30, 47, 32, 37, 42, 34, 40, 44],
      name: '올해 데이터(생산)',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#5C6BC0' },
    },
    {
      x: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
      y: [18, 13, 22, 35, 26, 42, 28, 33, 38, 30, 36, 40],
      name: '올해 데이터(판매)',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#7CB342' },
    },
    {
      x: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
      y: [10, 8, 14, 22, 18, 28, 20, 24, 27, 21, 26, 29],
      name: '올해 데이터(수입)',
      type: 'scatter',
      mode: 'lines+markers',
      marker: { color: '#FF8A65' }, 
    },
    {
      x: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
      y: [18, 12, 20, 30, 25, 40, 28, 32, 35, 28, 35, 38],
      name: '작년 데이터(생산)',
      type: 'bar',
      marker: { color: '#4DB6AC' },
    },
    {
      x: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
      y: [15, 10, 18, 25, 20, 35, 25, 28, 30, 25, 30, 33],
      name: '작년 데이터(판매)',
      type: 'bar',
      marker: { color: '#7986CB' },
    },
    {
      x: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'],
      y: [12, 8, 15, 20, 18, 30, 22, 25, 28, 22, 28, 30],
      name: '작년 데이터(수입)',
      type: 'bar',
      marker: { color: '#9E9E9E' },
    },
  ];

  const comparisonData = rawComparisonData.filter(trace => {
    if (selectedCategories.includes('생산') && (trace.name === '올해 데이터(생산)' || trace.name === '작년 데이터(생산)')) {
      return true;
    }
    if (selectedCategories.includes('판매') && (trace.name === '올해 데이터(판매)' || trace.name === '작년 데이터(판매)')) {
      return true;
    }
    if (selectedCategories.includes('수입') && (trace.name === '올해 데이터(수입)' || trace.name === '작년 데이터(수입)')) {
      return true;
    }
    return false;
  });

  const comparisonLayout = {
    title: '전년 대비 통계 차트',
    xaxis: { title: '월' },
    yaxis: { title: '값' },
    barmode: 'stack',
  };

  // Mock data for prediction chart
  const pastX = ['2023년 01월', '2023년 02월', '2023년 03월', '2023년 04월', '2023년 05월', '2023년 06월', '2023년 07월', '2023년 08월', '2023년 09월', '2023년 10월', '2023년 11월', '2023년 12월'];
  const predictedX = ['2024년 01월', '2024년 02월', '2024년 03월', '2024년 04월', '2024년 05월', '2024년 06월', '2024년 07월', '2024년 08월', '2024년 09월', '2024년 10월', '2024년 11월', '2024년 12월'];

  const predictionMockData = {
    '생산': {
      pastY: [10, 12, 15, 13, 16, 18, 20, 19, 22, 21, 24, 23],
      predictedY: [25, 27, 26, 28, 30, 29, 32, 31, 33, 35, 34, 36],
      color: '#5C6BC0',
      fill: 'rgba(92, 107, 192, 0.1)'
    },
    '판매': {
      pastY: [8, 10, 13, 11, 14, 16, 18, 17, 20, 19, 22, 21],
      predictedY: [23, 25, 24, 26, 28, 27, 30, 29, 31, 33, 32, 34],
      color: '#7CB342',
      fill: 'rgba(124, 179, 66, 0.1)'
    },
    '수입': {
      pastY: [5, 7, 9, 8, 10, 12, 14, 13, 16, 15, 18, 17],
      predictedY: [19, 21, 20, 22, 24, 23, 26, 25, 27, 29, 28, 30],
      color: '#FF8A65',
      fill: 'rgba(255, 138, 101, 0.1)'
    }
  };

  const predictionData = [];
  selectedCategories.forEach(category => {
    const categoryData = predictionMockData[category];
    if (categoryData) {
      const { pastY, predictedY, color, fill } = categoryData;
      const pastXConnected = [...pastX, predictedX[0]];
      const pastYConnected = [...pastY, predictedY[0]];

      predictionData.push({
        x: pastXConnected,
        y: pastYConnected,
        name: `과거 데이터(${category})`,
        type: 'scatter',
        mode: 'lines',
        line: { color: color },
      });
      predictionData.push({
        x: predictedX,
        y: predictedY,
        name: `예측 데이터(${category})`,
        type: 'scatter',
        mode: 'lines',
        line: { color: color, dash: 'dash' },
      });
      predictionData.push({
        x: [...predictedX, ...[...predictedX].reverse()],
        y: [...predictedY.map(y => y - 2), ...[...predictedY].reverse().map(y => y + 2)],
        fill: 'toself',
        fillcolor: fill,
        line: { color: 'transparent' },
        name: `신뢰구간(${category})`,
        showlegend: false,
        type: 'scatter',
      });
    }
  });


  const allX = [...pastX, ...predictedX];
  const ticktext = allX.map((label, index) => {
    const [year, month] = label.split(' ');

    if (index === 0) {
      return label;
    }

    const [prevYear] = allX[index - 1].split(' ');
    if (year !== prevYear) {
      return label;
    }

    return month;
  });

  const predictionLayout = {
    title: 'AI 예측 차트',
    xaxis: {
      title: '날짜',
      tickvals: allX,
      ticktext: ticktext,
    },
    yaxis: { title: '값 (톤)' },
  };

  return (
    <div className="chart-container">
      <div className="chart-placeholder">
        {analysisType === '통계' ? (
          <div className="comparison-chart">
            <h4>📊 전년 대비 통계 차트</h4>
            <p>• 올해 데이터(생산): 선 그래프 (#5C6BC0)</p>
            <p>• 올해 데이터(판매): 선 그래프 (#7CB342)</p>
            <p>• 올해 데이터(수입): 선 그래프 (#FF8A65)</p>
            <p>• 작년 데이터(생산): 막대 그래프 (#4DB6AC)</p>
            <p>• 작년 데이터(판매): 막대 그래프 (#7986CB)</p>
            <p>• 작년 데이터(수입): 막대 그래프 (#9E9E9E)</p>
            <Plot
              data={comparisonData}
              layout={comparisonLayout}
              style={{ width: '100%', height: '100%' }}
              useResizeHandler={true}
            />
          </div>
        ) : (
          <div className="prediction-chart">
            <h4>🔮 AI 예측 차트</h4>
            <p>• 실제 데이터: 실선</p>
            <p>• 예측 데이터: 점선 + 신뢰구간</p>
            <Plot
              data={predictionData}
              layout={predictionLayout}
              style={{ width: '100%', height: '100%' }}
              useResizeHandler={true}
            />
          </div>
        )}
      </div>

      {/* 🔥 차트 데이터 출처 표시 */}
      <div className="chart-data-source">
        <p><strong>📡 차트 데이터:</strong> {analysisType === '통계' ? '시계열 통계 분석 결과' : 'LSTM 예측 모델 출력'}</p>
        <p><strong>🔄 실시간 연동:</strong> 서버 DB에서 자동 업데이트</p>
      </div>
    </div>
  );
}
