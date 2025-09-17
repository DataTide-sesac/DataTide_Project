import React from 'react'
import { ResponsiveScatterPlot } from '@nivo/scatterplot'

export default function ScatterChartComponent({ data }) {
    return(
        <div style={{ height: 400 }}>
            <ResponsiveScatterPlot
                data={data}
                margin={{ top: 50, right: 60, bottom: 70, left: 60 }}
                xScale={{ type: 'linear', min: 'auto', max: 'auto' }}
                yScale={{ type: 'linear', min: 'auto', max: 'auto' }}
                axisBottom={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: '월',
                    legendPosition: 'middle',
                    legendOffset: 40,
                    tickValues: [0, 1, 2, 3, 4, 5],
                    tickFormat: d => `${d + 1}월`
                }}

                axisLeft={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: '예측 값',
                    legendPosition: 'middle',
                    legendOffset: -50
                }}
                
                enableGridX ={false}
                enableGridY ={false}

                nodeSize={15}
                useMesh={true}
                // colors={{ scheme: 'nivo' }}
                colors ={['#FFB777','#34b43bff','red']}
            />
        </div>
    )
}

