from DataTide_back.db.session import db_session
from typing import List

def get_fisheries_analysis_data(item_pk: int, years_to_query: List[int]):
    """
    Fetches and aggregates fisheries data from the database for analysis.
    """
    if not years_to_query:
        return []

    with db_session() as cursor:
        placeholders = ', '.join(['%s'] * len(years_to_query))
        sql = f"""
            SELECT
                EXTRACT(YEAR FROM month_date) AS year,
                EXTRACT(MONTH FROM month_date) AS month,
                SUM(production) AS production,
                SUM(sales) AS sales,
                SUM(inbound) AS inbound
            FROM
                item_retail
            WHERE
                item_pk = %s
                AND EXTRACT(YEAR FROM month_date) IN ({placeholders})
            GROUP BY
                year, month
            ORDER BY
                year, month
        """
        params = (item_pk,) + tuple(years_to_query)
        cursor.execute(sql, params)
        return cursor.fetchall()

def process_fisheries_statistics(item_pk: int, category_list: List[str], start_year: int, end_year: int):
    """
    Processes raw fisheries data to generate statistics for tables and charts.
    """
    years_to_query = sorted(list(set(list(range(start_year, end_year + 1)) + [end_year - 1])))
    results = get_fisheries_analysis_data(item_pk, years_to_query)

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
                'prevProduction': prev_year_data.get('production', 0),
                'prevSales': prev_year_data.get('sales', 0),
                'prevInbound': prev_year_data.get('inbound', 0),
            }

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