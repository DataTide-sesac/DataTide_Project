# routers/analysis.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional

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
        raise HTTPException(status_code=501, detail="Prediction analysis not yet implemented")
    else:
        raise HTTPException(status_code=400, detail=f"Invalid analysis_type: {analysis_type}")