import React from 'react';
import './Filter.css';

export default function SearchBar({
  fishItems,
  analysisOptions,
  dataCategories,
  yearOptions,
  period,
  setPeriod,
  selectedItem,
  setSelectedItem,
  selectedAnalysis,
  setSelectedAnalysis,
  selectedCategories,
  setSelectedCategories,
  fetchData,
  resetAll,
  canSearch,
  loading,
  error,
}) {
  return (
    <section className="filter-section">
      <div className="filter-container">
        
        {/* 품목 선택 (단일선택, 가로배치) */}
        <div className="filter-row">
          <label className="filter-label">품목</label>
          <div className="filter-options horizontal">
            {fishItems.map(item => (
              <button
                key={item.id}
                className={`option-btn ${selectedItem === item.id ? 'selected' : ''}`}
                onClick={() => setSelectedItem(item.id)}
                disabled={item.disabled}
              >
                {item.kr_name}
              </button>
            ))}
          </div>
        </div>

        {/* 분석 유형 (통계/예측, 단일선택, 가로배치) */}
        <div className="filter-row">
          <label className="filter-label">동향</label>
          <div className="filter-options horizontal">
            {analysisOptions.map(option => (
              <button
                key={option}
                className={`option-btn trend-button ${selectedAnalysis === option ? 'selected' : ''}`}
                onClick={() => setSelectedAnalysis(option)}
              >
                {option}
              </button>
            ))}
            <div className="category-group">
              {dataCategories.map(category => (
                <button
                  key={category}
                  className={`option-btn trend-button small ${selectedCategories.includes(category) ? 'selected' : ''}`}
                  onClick={() => {
                    if (selectedCategories.includes(category)) {
                      setSelectedCategories(prev => prev.filter(c => c !== category))
                    } else {
                      setSelectedCategories(prev => [...prev, category])
                    }
                  }}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="filter-row hint-row">
          <small className="filter-hint">* '생산', '판매', '수입'은 다중 선택이 가능합니다.</small>
        </div>
        

        {/* 기간 선택 (통계/예측 구분 없이) */}
        {selectedAnalysis === '통계' && (
          <div className="filter-row">
            <label className="filter-label">기간</label>
            <div className="period-controls">
              <select
                className="period-select"
                value={period.startYear}
                onChange={e => {
                  const val = parseInt(e.target.value, 10);
                  setPeriod(prev => ({ ...prev, startYear: val, endYear: Math.max(val, prev.endYear) }));
                }}
              >
                {yearOptions.map(year => (
                  <option key={year} value={year}>{year}년</option>
                ))}
              </select>
              <select
                className="period-select"
                value={period.startMonth}
                onChange={e => setPeriod(prev => ({ ...prev, startMonth: parseInt(e.target.value, 10) }))}
              >
                {Array.from({length: 12}, (_,i) => i+1).map(month => (
                  <option key={month} value={month}>{month}월</option>
                ))}
              </select>
              <span>~</span>
              <select
                className="period-select"
                value={period.endYear}
                onChange={e => {
                  const val = parseInt(e.target.value, 10);
                  setPeriod(prev => ({ ...prev, endYear: val, startYear: Math.min(val, prev.startYear) }));
                }}
              >
                {yearOptions.filter(year => year >= period.startYear).map(year => (
                  <option key={year} value={year}>{year}년</option>
                ))}
              </select>
              <select
                className="period-select"
                value={period.endMonth}
                onChange={e => setPeriod(prev => ({ ...prev, endMonth: parseInt(e.target.value, 10) }))}
              >
                {Array.from({length: 12}, (_,i) => i+1).map(month => (
                  <option key={month} value={month}>{month}월</option>
                ))}
              </select>
            </div>
          </div>
        )}

        </div>

        {/* 예측 정보 (예측일 때만 표시) */}
        {selectedAnalysis === '예측' && (
          <div className="prediction-info">
            <p><strong>기준일:</strong> 2025-07-30</p>
            <p><strong>과거 데이터:</strong> 6개월 (2025년 1월 ~ 7월)</p>
            <p><strong>예측 데이터:</strong> 6개월 (2025년 8월 ~ 2026년 1월)</p>
          </div>
        )}


        {/* 검색 버튼 */}
        <div className="search-section">
          <button
            type="button"
            className="option-btn reset-btn"
            onClick={resetAll}
          >
            선택초기화
          </button>
          <button
            className="option-btn reset-btn"
            onClick={fetchData}
            disabled={!canSearch || loading}
          >
            <span className="search-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
              </svg>
            </span>
            {loading ? '분석 중...' : '검색하기'}
          </button>
        </div>

        {/* 오류 메시지 */}
        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}
    </section>
  );
}