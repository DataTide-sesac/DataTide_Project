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

export default function ChartComponent({ data, analysisType, options }) {

  // --- Unified Chart.js Options ---
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: {
          font: {
            size: 14,
          },
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        mode: 'index',
        intersect: false,
      },
      datalabels: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: {
          font: {
            size: 14,
            weight: 'bold'
          },
        },
      },
      y: {
        ticks: {
          callback: function(value) {
            return value + '톤';
          }
        }
      },
    },
  };

  const statisticsOptions = {
    ...commonOptions,
    scales: {
      ...commonOptions.scales,
      x: {
        ...commonOptions.scales.x,
        stacked: false,
      },
      y: {
        ...commonOptions.scales.y,
        stacked: false,
      },
    }
  };

  return (
    <div className="chart-container">
      <div className="chart-placeholder">
        {analysisType === '통계' ? (
          isValidChartData(data) ? (
            <div className="comparison-chart" style={{height: '500px'}}>
              <Bar options={statisticsOptions} data={data} />
            </div>
          ) : (
            <p>통계 데이터를 불러오는 중이거나 데이터가 없습니다.</p>
          )
        ) : (
          isValidChartData(data) ? (
            <div className="prediction-chart" style={{height: '500px'}}>
              <Line options={options || commonOptions} data={data} />
            </div>
          ) : (
            <p>예측 데이터를 불러오는 중이거나 데이터가 없습니다.</p>
          )
        )}
      </div>
      <div className="chart-data-source">
      </div>
    </div>
  );
}