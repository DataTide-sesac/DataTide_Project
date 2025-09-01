import React from 'react'

export default function ChartComponent({ data, type }) {
  // 실제로는 Plotly.js나 Chart.js를 사용하여 구현
  // 여기서는 차트가 들어갈 자리만 표시

  return (
    <div className="chart-container">
      <div className="chart-placeholder">
        {type === 'comparison' ? (
          <div className="comparison-chart">
            <h4>📊 전년 대비 통계 차트</h4>
            <p>• 올해 데이터: 선 그래프 (파란색)</p>
            <p>• 작년 데이터: 막대 그래프 (회색)</p>
            <div className="chart-mock">
              [여기에 Plotly.js 차트가 렌더링됩니다]
              <br/>
              선그래프(올해) + 막대그래프(작년) 조합형 차트
            </div>
          </div>
        ) : (
          <div className="prediction-chart">
            <h4>🔮 AI 예측 차트</h4>
            <p>• 과거 데이터: 실선 (검은색)</p>
            <p>• 예측 데이터: 점선 (빨간색) + 신뢰구간</p>
            <div className="chart-mock">
              [여기에 Plotly.js 예측 차트가 렌더링됩니다]
              <br/>
              실제데이터(실선) + 예측데이터(점선) + 신뢰구간
            </div>
          </div>
        )}
      </div>

      {/* 🔥 차트 데이터 출처 표시 */}
      <div className="chart-data-source">
        <p><strong>📡 차트 데이터:</strong> {type === 'comparison' ? '시계열 통계 분석 결과' : 'LSTM 예측 모델 출력'}</p>
        <p><strong>🔄 실시간 연동:</strong> 서버 DB에서 자동 업데이트</p>
      </div>
    </div>
  )
}
