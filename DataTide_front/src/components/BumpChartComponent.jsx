import React from 'react';
import { ResponsiveBump } from '@nivo/bump';

const getStartOrder = (series) => {
  return [...series].sort((a, b) => {
    const ay = a.points?.[0]?.y || 0;
    const by = b.points?.[0]?.y || 0;
    return ay - by;
  });
};

const CustomEndLabel = ({ series }) => {
  if (!Array.isArray(series)) return null;

  // 시작 위치(y) 기준 정렬
  const sortedByStart = getStartOrder(series);

  // 정렬된 시리즈를 기반으로 라벨 렌더링
  return (
    <g>
      {sortedByStart.map(line => {
        if (!line.points || line.points.length === 0) return null;

        // 라벨을 시작점 기준으로 붙임
        const firstPoint = line.points[0];

        // 텍스트 위치: 시작점 기준 (x, y)
        const x = firstPoint.x - 40;
        const y = firstPoint.y;

        // 텍스트 내용
        const text = line.id;

        // 스타일
        const fontSize = 20;
        const rectWidth = text.length * 15 + 20;
        const rectHeight = fontSize + 15;

        return (
          <g key={line.id} transform={`translate(${x}, ${y})`}>
            <rect
              x={-rectWidth}
              y={-rectHeight / 2}
              width={rectWidth}
              height={rectHeight}
              fill="white"
              stroke={line.color}
              strokeWidth={1}
              rx={4}
              ry={4}
              opacity={0.8}
            />
            <text
              x={-rectWidth / 2}
              y={0}
              alignmentBaseline="middle"
              textAnchor="middle"
              fontSize={fontSize}
              fill={line.color}
              fontWeight="bold"
            >
              {text}
            </text>
          </g>
        );
      })}
    </g>
  );
};

export default function BumpChartComponent({ data }) {
  // 데이터가 없거나, 데이터 형식이 올바르지 않으면 차트를 렌더링하지 않습니다.
  if (!data || !Array.isArray(data) || data.length === 0 || !data[0].data) {
    return <div style={{ height: 400, textAlign: 'center', lineHeight: '400px' }}>Bump Chart 데이터를 불러오는 중입니다...</div>;
  }

  // x축 라벨(눈금)의 개수를 계산합니다.
  const tickCount = data[0].data.length;

  // 라벨 개수에 따라 동적으로 폰트 크기를 계산합니다.
  // 기본 14px, 8개 초과 시 1개마다 1px씩 감소, 최소 8px
  const dynamicFontSize = Math.max(4, 22 - Math.max(0, tickCount - 4));

  return (
    <div style={{ height: 400 }}>
      <ResponsiveBump
        data={data}
        colors={['#FFB777', '#34b43bff', '#278adbff']}
        // colors={{ scheme: 'nivo' }}
        lineWidth={3}
        xPadding={0.4}
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
        pointBorderColor='gray'
        margin={{ top: 40, right: 40, bottom: 40, left: 80 }}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: '',
          legendPosition: 'middle',
          legendOffset: -36,
        }}
        axisTop={null}
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
        }}
        enableGridX ={false}
        enableGridY ={false}
        layers={['grid','axes', 'lines','points', CustomEndLabel]}
      />
    </div>
  );
}