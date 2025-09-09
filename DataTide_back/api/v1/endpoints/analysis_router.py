# routers/analysis.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional

from DataTide_back.core.database import get_db
from DataTide_back.db.models.item import Item
from DataTide_back.db.models.item_retail import ItemRetail

router = APIRouter(tags=["analysis"])

@router.get("/fisheries-analysis")
def get_fisheries_analysis(
    db: Session = Depends(get_db),
    item: str = None,
    analysis_type: str = None,
    categories: str = None, # Comma-separated string
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    base_date: Optional[str] = None,
):
    if not all([item, analysis_type, categories]):
        raise HTTPException(status_code=400, detail="Missing required query parameters: item, analysis_type, categories")

    item_obj = db.query(Item).filter(Item.item_name == item).first()
    if not item_obj:
        raise HTTPException(status_code=404, detail=f"Item '{item}' not found")
    
    item_pk = item_obj.item_pk
    category_list = [c.strip() for c in categories.split(',')]

    if analysis_type == '통계':
        if not all([start_year, end_year]):
            raise HTTPException(status_code=400, detail="'통계' analysis requires start_year and end_year")

        # Query data for all years in the range [start_year, end_year]
        # and also for (end_year - 1) for previous year comparison
        years_to_query = list(range(start_year, end_year + 1)) + [end_year - 1]
        years_to_query = sorted(list(set(years_to_query))) # Remove duplicates and sort

        query = (
            db.query(
                extract('year', ItemRetail.month_date).label('year'),
                extract('month', ItemRetail.month_date).label('month'),
                func.sum(ItemRetail.production).label('production'),
                func.sum(ItemRetail.sales).label('sales'),
                func.sum(ItemRetail.inbound).label('inbound')
            )
            .filter(
                ItemRetail.item_pk == item_pk,
                extract('year', ItemRetail.month_date).in_(years_to_query)
            )
            .group_by('year', 'month')
            .order_by('year', 'month')
        )
        
        results = query.all()

        # Process results for table and chart
        data_by_year_month = {}
        for row in results:
            year_key = row.year
            month_key = row.month
            if year_key not in data_by_year_month:
                data_by_year_month[year_key] = {}
            data_by_year_month[year_key][month_key] = {
                'production': row.production,
                'sales': row.sales,
                'inbound': row.inbound
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

                # Calculate previous year data and change percentages
                entry['prevProduction'] = prev_year_data.get('production', 0)
                entry['prevSales'] = prev_year_data.get('sales', 0)
                entry['prevInbound'] = prev_year_data.get('inbound', 0)

                def calculate_change(current, prev):
                    if prev == 0: # Avoid division by zero
                        return 0 if current == 0 else 100 # If prev is 0, and current is not, it's 100% increase
                    return ((current - prev) / prev) * 100

                entry['productionChange'] = calculate_change(entry['production'], entry['prevProduction'])
                entry['salesChange'] = calculate_change(entry['sales'], entry['prevSales'])
                entry['inboundChange'] = calculate_change(entry['inbound'], entry['prevInbound'])
                
                table_data.append(entry)

        # Format for chartData
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
                # Current year line chart
                traces.append({
                    'x': months_kr,
                    'y': [data_by_year_month.get(end_year, {}).get(m, {}).get(category_en) for m in range(1, 13)],
                    'name': f'{end_year}({category_kr})',
                    'type': 'scatter',
                    'mode': 'lines+markers',
                    'marker': {'color': colors[category_kr]},
                })
                # Previous year bar chart
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

