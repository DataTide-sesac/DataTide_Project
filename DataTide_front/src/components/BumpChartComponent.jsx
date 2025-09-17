import React from 'react';
import { ResponsiveBump } from '@nivo/bump';

// 이 컴포넌트는 차트 끝에 품목명을 표시하는 역할을 합니다.
const CustomEndLabel = ({ series }) => (
  <g>
    {Array.isArray(series) &&
      series.map(line => {
        if (!line.points || line.points.length === 0) {
          return null;
        }
        const lastPoint = line.points[line.points.length - 1];
        return (
          <text
            key={line.id}
            x={lastPoint.x * 1.12} // 라인 끝에서 약간의 여백을 줍니다.
            y={lastPoint.y}
            alignmentBaseline="middle"
            fontSize={14} // 폰트 크기를 적절하게 조절합니다.
            fill={line.color}
            fontWeight="bold"
          >
            {line.id}
          </text>
        );
      })}
  </g>
);

export default function BumpChartComponent({ data }) {
  // 데이터가 없거나, 데이터 형식이 올바르지 않으면 차트를 렌더링하지 않습니다.
  if (!data || !Array.isArray(data) || data.length === 0 || !data[0].data) {
    return <div style={{ height: 400, textAlign: 'center', lineHeight: '400px' }}>Bump Chart 데이터를 불러오는 중입니다...</div>;
  }

  // x축 라벨(눈금)의 개수를 계산합니다.
  const tickCount = data[0].data.length;

  // 라벨 개수에 따라 동적으로 폰트 크기를 계산합니다.
  // 기본 14px, 8개 초과 시 1개마다 1px씩 감소, 최소 8px
  const dynamicFontSize = Math.max(8, 14 - Math.max(0, tickCount - 8));

  return (
    <div style={{ height: 400 }}>
      <ResponsiveBump
        data={data}
        colors={['#FFB777', '#34b43bff', '#278adbff']}
        lineWidth={3}
        activeLineWidth={6}
        inactiveLineWidth={3}
        pointSize={20}
        activePointSize={16}
        inactivePointSize={0}
        pointBorderWidth={3}
        axisLeft={null}
        axisRight={null}
        inactiveOpacity={0.15}
        pointColor={{ from: 'serie.color' }}
        activePointBorderWidth={3}
        pointBorderColor={{ from: 'serie.color' }}
        margin={{ top: 40, right: 120, bottom: 40, left: 40 }}
        axisTop={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: '',
          legendPosition: 'middle',
          legendOffset: -36,
        }}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: '',
          legendPosition: 'middle',
          legendOffset: 32,
        }}
        // 동적으로 계산된 폰트 크기를 theme prop을 통해 적용합니다.
        theme={{
          axis: {
            ticks: {
              text: {
                fontSize: dynamicFontSize,
                fill: '#333333',
              },
            },
          },
          grid: {
            line: {
              stroke: '#dddddd',
              strokeDasharray: '4 4',
            },
          },
        }}
        layers={['grid', 'axes', 'lines', 'points', CustomEndLabel]}
      />
    </div>
  );
}