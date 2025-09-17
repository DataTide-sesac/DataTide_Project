import React from 'react'
import { ResponsiveScatterPlot } from '@nivo/scatterplot'

export default function BubbleChartComponent({ data }) {
    return(
            <div style={{ height: 400 }}>
                <ResponsiveScatterPlot
                    data={data}
                    margin={{ top: 50, right: 60, bottom: 70, left: 60 }}
                    xScale={{ type: 'linear', min: 'auto', max: 'auto' }}
                    yScale={{ type: 'linear', min: 'auto', max: 'auto' }}
                    axisBottom={{
                        tickSize: 12,
                        tickPadding: 5,
                        tickRotation: 0,
                        legend: '월',
                        legendPosition: 'middle',
                        legendOffset: 40,
                        tickValues: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
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
                    
                    nodeSize={d => d.data.size * 1.5}
                    // nodeSize={d => d.data.size !== 0 ? }
                    // nodeSize={d => d.data.y * 10}
                    useMesh={true}
                    // colors={{ scheme: 'nivo' }}
                    colors ={['#ffb77769','#34b43a71','#ff080828']}
                />
            </div>
        )

}

