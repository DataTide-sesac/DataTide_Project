
from fastapi.testclient import TestClient
import pytest

# /api/fisheries-analysis 엔드포인트 테스트
def test_get_fisheries_analysis_success(client: TestClient, monkeypatch):
    """
    분석 API 성공 케이스 (200 OK) 테스트
    - 서비스 함수를 monkeypatch를 이용해 가짜 데이터로 대체합니다.
    """
    # 가짜 item_crud.get_item_by_name 함수 정의
    def mock_get_item_by_name(item_name):
        if item_name == "광어":
            return {"item_pk": 1, "item_name": "광어"}
        return None

    # 가짜 analysis_service.get_fisheries_analysis_data 함수 정의
    def mock_get_analysis_data(item_pk, years):
        # 실제 DB 결과와 유사한 형태의 샘플 데이터 반환
        return [
            {"year": 2023, "month": 1, "production": 100, "sales": 80, "inbound": 20},
            {"year": 2022, "month": 1, "production": 90, "sales": 70, "inbound": 15},
        ]

    # monkeypatch를 사용하여 실제 함수를 가짜 함수로 교체
    monkeypatch.setattr("DataTide_back.services.item_crud.get_item_by_name", mock_get_item_by_name)
    monkeypatch.setattr("DataTide_back.services.analysis_service.get_fisheries_analysis_data", mock_get_analysis_data)

    # API 요청
    response = client.get(
        "/api/fisheries-analysis?item=광어&analysis_type=통계&categories=생산,판매&start_year=2023&end_year=2023"
    )

    # 결과 검증
    assert response.status_code == 200
    data = response.json()
    assert "tableData" in data
    assert "chartData" in data
    assert len(data["tableData"]) > 0
    assert len(data["chartData"]) > 0

def test_get_fisheries_analysis_missing_params(client: TestClient):
    """
    필수 파라미터 누락 시 (400 Bad Request) 테스트
    """
    response = client.get("/api/fisheries-analysis?item=광어&analysis_type=통계")
    assert response.status_code == 400
    assert response.json() == {"detail": "Missing required query parameters: item, analysis_type, categories"}

def test_get_fisheries_analysis_item_not_found(client: TestClient, monkeypatch):
    """
    존재하지 않는 품목 요청 시 (404 Not Found) 테스트
    """
    # item_crud.get_item_by_name이 항상 None을 반환하도록 설정
    monkeypatch.setattr("DataTide_back.services.item_crud.get_item_by_name", lambda item_name: None)

    response = client.get(
        "/api/fisheries-analysis?item=없는생선&analysis_type=통계&categories=생산&start_year=2023&end_year=2023"
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Item '없는생선' not found"}

def test_get_fisheries_analysis_not_implemented(client: TestClient, monkeypatch):
    """
    '예측' 기능 요청 시 (501 Not Implemented) 테스트
    """
    # '예측' 요청 시에도 item_pk는 필요하므로 get_item_by_name은 mock 처리
    monkeypatch.setattr("DataTide_back.services.item_crud.get_item_by_name", lambda item_name: {"item_pk": 1, "item_name": "광어"})

    response = client.get(
        "/api/fisheries-analysis?item=광어&analysis_type=예측&categories=생산"
    )
    assert response.status_code == 501
    assert response.json() == {"detail": "Prediction analysis not yet implemented"}

def test_get_fisheries_analysis_invalid_type(client: TestClient, monkeypatch):
    """
    잘못된 analysis_type 요청 시 (400 Bad Request) 테스트
    """
    monkeypatch.setattr("DataTide_back.services.item_crud.get_item_by_name", lambda item_name: {"item_pk": 1, "item_name": "광어"})

    response = client.get(
        "/api/fisheries-analysis?item=광어&analysis_type=잘못된타입&categories=생산"
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid analysis_type: 잘못된타입"}
