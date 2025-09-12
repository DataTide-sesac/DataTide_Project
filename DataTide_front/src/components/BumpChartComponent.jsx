import React from 'react';
import { ResponsiveBump } from '@nivo/bump'; // Nivo Bump Chart 사용 예시

const CustomEndLabel = ({series}) => (
  <g>
    {Array.isArray(series) &&
      series.map(line => {
        const lastPoint = line.points[line.points.length - 1];
        return (
          <text
            key={line.id}               // React key prop은 line.id 사용
            x={lastPoint.x * 1.1}
            y={lastPoint.y}
            alignmentBaseline="middle"
            fontSize={18}
            fill={line.color}
            fontWeight="bold"
          >
            {line.id}                 {/* 화면에 표시할 텍스트도 line.id 사용 */}
          </text>
        );
      })}
  </g>
);


export default function BumpChartComponent({ data }) {
  return (
    <div style={{ height: 400 }}>
      <ResponsiveBump
        data={data}
        colors ={['#FFB777','#34b43bff','#278adbff']}
        // colors={{ scheme: 'nivo' }}
        lineWidth={3}
        activeLineWidth={6}
        inactiveLineWidth={3}
        pointSize={20}
        activePointSize={16}
        inactivePointSize={0}
        pointBorderWidth={3}
        axisLeft={null}
        axisRight={null}
        margin={{ top: 40, right: 100, bottom: 40, left: 100 }}
        axisTop={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          tickValues: 6,
          legendPosition: 'middle',
          legendOffset: -36,
          tickTextColor: '#333',
          tick: {
            text: {
              fontSize: 30,  // 폰트 크기 지정
            }
          }
        }}
        axisBottom={{
          tickSize: 10,
          tickPadding: 5,
          tickRotation: 0,
          tickTextColor: '#333',
          tick: {
            text: {
              fontSize: 30,
            }
          }
        }}

        //
        theme={{
          axis: {
            ticks: {
              text: {
                fontSize: 16,  // 축 눈금 폰트 크기 지정
                fill: '#333',  // 텍스트 색상 지정 가능
              }
            },
            legend: {
              text: {
                fontSize: 16,
                fill: '#333',
              }
            },
            labels: {
              text: {
                fontSize: 16,
                fontWeight: 600,
                fill: "#333",
              }
            }
          }
        }}
        //
        layers={['grid', 'axes', 'lines','series', 'points', CustomEndLabel]}
      />
    </div>
  );
}
