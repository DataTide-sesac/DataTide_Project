import React, { useState, useEffect } from 'react';
import { Bar, Line } from 'react-chartjs-2';
import ChartDataLabels from 'chartjs-plugin-datalabels'; //데이터 숫자 표기
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { color } from 'chart.js/helpers';
import { isValidChartData} from '../utils/index';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartDataLabels //데이터 숫자 표기
);

export default function ChartComponent({ data, analysisType, selectedCategories }) {
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // --- Chart.js Options for Statistics Chart ---
  const chartJsOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: {
          font: {
            size: 14, // 사용자가 요청한 크기
          },
        },
      },

      title: {
        display: false, // Using custom title outside the chart
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
      datalabels: {
        display: false, // ➡️ 모든 라벨을 기본적으로 숨김
      },
    },
    scales: {
      x: {
        stacked: true,
        ticks: {
          font: {
            size: 14,
            weight: 'bold'
          },
        },
      },
      y: {
        stacked: true,
        ticks: {
          callback: function(value) {
            return value + '톤';
          }
        }
      },
    },
  };

  // --- Chart.js Data and Options for Prediction Chart ---
  const fullPastX = ['2023년 01월', '2023년 02월', '2023년 03월', '2023년 04월', '2023년 05월', '2023년 06월', '2023년 07월', '2023년 08월', '2023년 09월', '2023년 10월', '2023년 11월', '2023년 12월'];
  const fullPredictedX = ['2024년 01월', '2024년 02월', '2024년 03월', '2024년 04월', '2024년 05월', '2024년 06월', '2024년 07월', '2024년 08월', '2024년 09월', '2024년 10월', '2024년 11월', '2024년 12월'];

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

  const pastX = fullPastX.slice(-6);
  const predictedX = fullPredictedX.slice(0, 6);
  const allX = [...pastX, ...predictedX];
  const ticktext = allX.map((label, index) => {
    const [year, month] = label.split(' ');
    if (index === 0) return label;
    const [prevYear] = allX[index - 1].split(' ');
    if (year !== prevYear) return label;
    return month;
  });

  const predictionChartJsData = {
    labels: allX,
    datasets: []
  };

  selectedCategories.forEach(category => {
    const trimmedCategory = category.trim();
    const categoryData = predictionMockData[trimmedCategory];
    if (categoryData) {
      const { color, fill } = categoryData;
      const pastY = categoryData.pastY.slice(-6);
      const predictedY = categoryData.predictedY.slice(0, 6);

      // Past data connected to predicted
      predictionChartJsData.datasets.push({
        label: `과거 ${category}`,
        data: [...pastY, predictedY[0], ...Array(predictedY.length - 1).fill(null)],
        borderColor: color,
        backgroundColor: color,
        fill: false,
        type: 'line',
        tension: 0.1,
        pointRadius: 6,
        pointHoverRadius: 7,
        borderWidth:3.5,
      });

      // Predicted data
      predictionChartJsData.datasets.push({
        label: `예측 ${category}`,
        data: [...Array(pastY.length).fill(null), ...predictedY],
        borderColor: color,
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        fill: false,
        type: 'line',
        tension: 0.1,
        // pointBorderDash: [5, 5],
        pointRadius: 12,
        pointHoverRadius: 15,
        pointBorderWidth: 5,
        pointBorderColor: color,
      });

      // Confidence Interval - upper bound
      predictionChartJsData.datasets.push({
        label: `신뢰구간(${category})`,
        data: [...Array(pastY.length).fill(null), ...predictedY.map(y => y + 2)],
        borderColor: 'transparent',
        backgroundColor: 'transparent',
        pointRadius: 0,
        fill: false,
      });

      // Confidence Interval - lower bound
      predictionChartJsData.datasets.push({
        label: `신뢰구간(${category})`,
        data: [...Array(pastY.length).fill(null), ...predictedY.map(y => y - 2)],
        borderColor: 'transparent',
        backgroundColor: fill,
        pointRadius: 0,
        fill: '-1', // Fill to previous dataset (upper bound)
      });
    }
  });

  const predictionChartJsOptions = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
        line: {
            borderWidth: 8
        }
    },
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        onClick: function(e, legendItem, legend) {
            const chart = legend.chart;
            const index = legendItem.datasetIndex;

            // Determine the new hidden state from the clicked item's metadata
            const meta = chart.getDatasetMeta(index);
            const newHiddenState = meta.hidden === null ? !chart.data.datasets[index].hidden : null;

            // Find the start index of the group of 4 datasets for this category
            const groupStartIndex = Math.floor(index / 4) * 4;

            const linkedIndices = [
                groupStartIndex,     // Past
                groupStartIndex + 1, // Prediction
                groupStartIndex + 2, // CI Upper
                groupStartIndex + 3  // CI Lower
            ];

            linkedIndices.forEach(function(i) {
                const datasetMeta = chart.getDatasetMeta(i);
                if (datasetMeta) {
                    datasetMeta.hidden = newHiddenState;
                }
            });

            chart.update();
        },
        labels: {
            filter: function(legendItem) {
                return !legendItem.text.includes('신뢰구간');
            }
        }
      },
      // title: {
      //   display: true,
      //   // text: '🔮 AI 예측 차트',
      //   font: { size: 20 }
      // },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
      datalabels: {
        display: function(context) {
          const datasetLabel = context.dataset.label;
          return (datasetLabel.includes('과거') || datasetLabel.includes('예측'));
        },
        align: 'top',
        color: 'black',
        padding:{bottom:15},
        
        font: {
          // weight: 'bold',
          size: 15
        },
        formatter: Math.round
      }
    },
    scales: {
      x: {
        ticks: {
            callback: function(value, index) {
                return ticktext[index];
            },
            font: {
                weight: 'bold'
            }
        }
      },
      y: {
        title: {
            display: true,
            text: '단위(톤)',
            font: {
                size: 15
            }
        }
      },
    },
  };

  return (
    <div className="chart-container">
      <div className="chart-placeholder">
        {analysisType === '통계' ? (
          isValidChartData(data)?(
          <div>
            <div className="comparison-chart" style={{height: '500px'}}>
              <Bar options={chartJsOptions} data={data} />
            </div>
            {/* <div className="comparison-chart" style={{height: '500px'}}>
              <h4>📊 전년 대비 통계 차트</h4>
              <Bar options={chartJsOptions} data={data} />
            </div> */}
          </div>
          ):(console.log('데이터없음'))
        ) : (
          <div className="prediction-chart" style={{height: '500px'}}>
            <Line options={predictionChartJsOptions} data={predictionChartJsData} />
          </div>
        )}
      </div>
      <div className="chart-data-source">
      </div>
    </div>
  );
}