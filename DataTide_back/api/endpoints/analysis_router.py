# routers/analysis.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from fastapi.responses import StreamingResponse

# Import new pymysql-based services
from DataTide_back.services import item_crud
from DataTide_back.services import analysis_service

router = APIRouter(tags=["analysis"])

@router.get("/fisheries-analysis")
def get_fisheries_analysis(
    item: str = None,
    analysis_type: str = None,
    categories: str = None, # Comma-separated string
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    base_date: Optional[str] = None,
):
    if not all([item, analysis_type, categories]):
        raise HTTPException(status_code=400, detail="Missing required query parameters: item, analysis_type, categories")

    # Use the new service to get item info
    item_obj = item_crud.get_item_by_name(item_name=item)
    if not item_obj:
        raise HTTPException(status_code=404, detail=f"Item '{item}' not found")
    
    item_pk = item_obj['item_pk']
    category_list = [c.strip() for c in categories.split(',')]

    if analysis_type == '통계':
        if not all([start_year, end_year]):
            raise HTTPException(status_code=400, detail="'통계' analysis requires start_year and end_year")

        # Delegate all processing to the service layer
        return analysis_service.process_fisheries_statistics(
            item_pk=item_pk,
            category_list=category_list,
            start_year=start_year,
            end_year=end_year
        )

    elif analysis_type == '예측':
        if not base_date:
            raise HTTPException(status_code=400, detail="'예측' analysis requires a base_date")
        return analysis_service.get_prediction_chart_data(
            item_pk=item_pk,
            category_list=category_list,
            base_date_str=base_date
        )
    else:
        raise HTTPException(status_code=400, detail=f"Invalid analysis_type: {analysis_type}")

@router.get("/prediction-data")
def get_prediction_data(
    items: str,
    location: Optional[str] = None,
    base_date: str = None,
):
    item_list = [item.strip() for item in items.split(',')]
    return analysis_service.get_prediction_data(
        item_names=item_list,
        location_name=location,
        base_date=base_date
    )

@router.get("/stats-data")
def get_stats_data(
    items: str,
    start_year: int,
    end_year: int,
    location: Optional[str] = None,
):
    item_list = [item.strip() for item in items.split(',')]
    return analysis_service.get_stats_data(
        item_names=item_list,
        start_year=start_year,
        end_year=end_year,
        location_name=location
    )

@router.get("/download/excel")
def download_excel(
    type: str,
    items: str,
    location: Optional[str] = None,
    base_date: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
):
    item_list = [item.strip() for item in items.split(',')]
    
    if type == "prediction":
        if not base_date:
            raise HTTPException(status_code=400, detail="base_date is required for prediction type")
        file_stream, filename = analysis_service.create_prediction_excel(item_list, location, base_date)
    elif type == "stats":
        if not start or not end:
            raise HTTPException(status_code=400, detail="start and end years are required for stats type")
        file_stream, filename = analysis_service.create_stats_excel(item_list, location, start, end)
    else:
        raise HTTPException(status_code=400, detail="Invalid type for excel download")

    return StreamingResponse(file_stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename={filename}"})