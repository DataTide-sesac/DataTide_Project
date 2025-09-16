# routers/analysis.py
from fastapi import APIRouter, HTTPException
from typing import List, Optional

# Import new pymysql-based services
from services import item_crud
from services import analysis_service

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

        years_to_query = sorted(list(set(list(range(start_year, end_year + 1)) + [end_year - 1])))

        # Use the new analysis service to get data
        results = analysis_service.get_fisheries_analysis_data(item_pk, years_to_query)

        # The rest of the data processing logic remains the same
        data_by_year_month = {}
        for row in results:
            year_key = row['year']
            month_key = row['month']
            if year_key not in data_by_year_month:
                data_by_year_month[year_key] = {}
            data_by_year_month[year_key][month_key] = {
                'production': row['production'],
                'sales': row['sales'],
                'inbound': row['inbound']
            }

        table_data = []
        all_months = list(range(1, 13))

        for year in range(start_year, end_year + 1):
            for month in all_months:
                current_data = data_by_year_month.get(year, {}).get(month, {})
                prev_year_data = data_by_year_month.get(year - 1, {}).get(month, {})

                entry = {
                    'period': f'{year}-{month:02d}',
                    'production': current_data.get('production', 0),
                    'sales': current_data.get('sales', 0),
                    'inbound': current_data.get('inbound', 0),
                }

                entry['prevProduction'] = prev_year_data.get('production', 0)
                entry['prevSales'] = prev_year_data.get('sales', 0)
                entry['prevInbound'] = prev_year_data.get('inbound', 0)

                def calculate_change(current, prev):
                    if prev == 0:
                        return 0 if current == 0 else 100
                    return ((current - prev) / prev) * 100

                entry['productionChange'] = calculate_change(entry['production'], entry['prevProduction'])
                entry['salesChange'] = calculate_change(entry['sales'], entry['prevSales'])
                entry['inboundChange'] = calculate_change(entry['inbound'], entry['prevInbound'])
                
                table_data.append(entry)

        traces = []
        months_kr = [f'{i}월' for i in range(1, 13)]
        category_map = {
            "생산": "production",
            "판매": "sales",
            "수입": "inbound"
        }
        colors = {"생산": "#1565C0", "판매": "#388E3C", "수입": "#F57C00"}
        bar_colors = {"생산": "rgba(100, 181, 246, 0.65)", "판매": "rgba(129, 199, 132, 0.65)", "수입": "rgba(255, 183, 77, 0.65)"}

        for category_kr, category_en in category_map.items():
            if category_kr in category_list:
                traces.append({
                    'x': months_kr,
                    'y': [data_by_year_month.get(end_year, {}).get(m, {}).get(category_en) for m in range(1, 13)],
                    'name': f'{end_year}({category_kr})',
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'marker': {'color': colors[category_kr]},
                })
                traces.append({
                    'x': months_kr,
                    'y': [data_by_year_month.get(end_year - 1, {}).get(m, {}).get(category_en) for m in range(1, 13)],
                    'name': f'{end_year - 1}({category_kr})',
                    'type': 'bar',
                    'marker': {'color': bar_colors[category_kr]},
                })

        return {"tableData": table_data, "chartData": traces}

    elif analysis_type == '예측':
        raise HTTPException(status_code=501, detail="Prediction analysis not yet implemented")
    else:
        raise HTTPException(status_code=400, detail=f"Invalid analysis_type: {analysis_type}")

