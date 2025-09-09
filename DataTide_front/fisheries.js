1. 신규 API 엔드포인트 정보
  대시보드에서 필요한 모든 데이터(테이블, 차트)는 이제 아래의 단일 API 엔드포인트를 통해 제공됩니다.

   - URL: GET /api/fisheries-analysis
  `json
      {
        "tableData": [
          { "year": 2024, "month": 1, "production": 123, ... },
          ...
        ],
        "chartData": [
          { "x": ["1월", ...], "y": [123, ...], "name": "2024(생산)", ... },
          ...
        ]
      }
      `
      -   tableData: 테이블에 표시될 데이터 배열
      -   chartData: Plotly.js 차트에 바로 사용할 수 있는 "trace" 객체 배열

  ### 2. 프론트엔드 주요 수정 사항
  #### A. 상수 데이터 변경 (src/constants/index.js)
   - FISH_ITEMS 배열의 구조가 변경되었습니다.
  변경 후:
  { id: 'KDFSH01', name: 'Mackerel', kr_name: '고등어' }

  #### B. API 호출 로직 수정 (src/pages/DashboardPage.jsx)
   - fetchData 함수에서 Mock 데이터를 생성하는 로직을 모두 제거하고, 실제 API를 호출하는 fetchFisheriesData 함수를 사용해야 합니다.
  C. UI 텍스트 표시 수정 (모든 관련 컴포넌트)
   - DashboardPage.jsx, SearchBar.jsx 등 품목 이름이 화면에 표시되는 모든 곳에서 .name 대신 .kr_name 속성을 사용하도록 수정해야 합니다. (예: 검색 버튼, 차트 제목 등)