# services/analysis_service.py
from DataTide_back.db.session import db_session
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta
from DataTide_back.services import item_crud

def get_prediction_chart_data(item_pk: int, category_list: List[str], base_date_str: str):
    """
    Fetches past and predicted data to generate data for prediction charts.
    """
    base_date = datetime.strptime(base_date_str, '%Y-%m-%d').date()
    past_start_date = base_date - relativedelta(months=6)
    
    # Fetch past data
    with db_session() as cursor:
        sql_past = """
            SELECT month_date, production, sales, inbound
            FROM item_retail
            WHERE item_pk = %s AND month_date >= %s AND month_date < %s
            ORDER BY month_date
        """
        cursor.execute(sql_past, (item_pk, past_start_date, base_date))
        past_results = cursor.fetchall()

    # Fetch predicted data
    with db_session() as cursor:
        sql_predict = """
            SELECT month_date, production, sales, inbound
            FROM item_predict
            WHERE item_pk = %s AND month_date >= %s
            ORDER BY month_date
            LIMIT 6
        """
        cursor.execute(sql_predict, (item_pk, base_date))
        predict_results = cursor.fetchall()

    # Add dataType and confidence
    for row in past_results:
        row['dataType'] = '실제'
        row['confidence'] = 100
        row['period'] = row['month_date'].strftime('%Y-%m')
        del row['month_date']

    for row in predict_results:
        row['dataType'] = '예측'
        row['confidence'] = 95 # Dummy value
        row['period'] = row['month_date'].strftime('%Y-%m')
        del row['month_date']

    # Combine and format data
    table_data = past_results + predict_results
    
    # Create chart traces
    traces = []
    category_map = {"생산": "production", "판매": "sales", "수입": "inbound"}
    
    past_dates = [r['period'] for r in past_results]
    predict_dates = [r['period'] for r in predict_results]
    
    for category_kr, category_en in category_map.items():
        if category_kr in category_list:
            # Past data trace
            traces.append({
                'x': past_dates,
                'y': [r.get(category_en) for r in past_results],
                'name': f'과거 {category_kr}',
                'type': 'scatter',
                'mode': 'lines'
            })
            # Predicted data trace
            traces.append({
                'x': predict_dates,
                'y': [r.get(category_en) for r in predict_results],
                'name': f'예측 {category_kr}',
                'type': 'scatter',
                'mode': 'lines',
                'line': {'dash': 'dash'}
            })

    return {"tableData": table_data, "chartData": traces}

def get_fisheries_analysis_data(item_pk: int, start_year: int, start_month: int, end_year: int, end_month: int):
    """
    Fetches and aggregates fisheries data from the database for a specific date range.
    """
    start_date = f"{start_year}-{start_month:02d}-01"
    # Calculate the end date as the first day of the month after the end_month
    end_date_dt = datetime(end_year, end_month, 1) + relativedelta(months=1)
    end_date = end_date_dt.strftime('%Y-%m-%d')

    with db_session() as cursor:
        sql = """
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
                AND month_date >= %s
                AND month_date < %s
            GROUP BY
                year, month
            ORDER BY
                year, month
        """
        params = (item_pk, start_date, end_date)
        cursor.execute(sql, params)
        return list(cursor.fetchall())

def process_fisheries_statistics(item_pk: int, category_list: List[str], start_year: int, end_year: int, start_month: Optional[int] = None, end_month: Optional[int] = None):
    """
    Processes raw fisheries data to generate statistics for tables and charts.
    """
    sm = start_month if start_month is not None else 1
    em = end_month if end_month is not None else 12

    # Fetch data for the selected period
    current_period_results = get_fisheries_analysis_data(item_pk, start_year, sm, end_year, em)

    # Fetch data for the previous year's period for comparison
    prev_period_results = get_fisheries_analysis_data(item_pk, start_year - 1, sm, end_year - 1, em)

    # Organize data by year and month for easy lookup
    data_by_year_month = {}
    for row in current_period_results + prev_period_results:
        year_key = row['year']
        month_key = row['month']
        if year_key not in data_by_year_month:
            data_by_year_month[year_key] = {}
        data_by_year_month[year_key][month_key] = {
            'production': row['production'],
            'sales': row['sales'],
            'inbound': row['inbound']
        }

    # Create a list of all (year, month) tuples in the selected range
    all_periods = []
    current_date = datetime(start_year, sm, 1)
    end_date_loop = datetime(end_year, em, 1)
    while current_date <= end_date_loop:
        all_periods.append((current_date.year, current_date.month))
        current_date += relativedelta(months=1)

    # --- Generate Table Data ---
    table_data = []
    for year, month in all_periods:
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

    # --- Generate Chart Data ---
    traces = []
    # Use a consistent format for x-axis labels, e.g., 'YYYY-MM'
    chart_labels = [f'{p[0]}-{p[1]:02d}' for p in all_periods]

    category_map = {
        "생산": "production",
        "판매": "sales",
        "수입": "inbound"
    }
    colors = {"생산": "#1565C0", "판매": "#388E3C", "수입": "#F57C00"}
    bar_colors = {"생산": "rgba(100, 181, 246, 0.65)", "판매": "rgba(129, 199, 132, 0.65)", "수입": "rgba(255, 183, 77, 0.65)"}

    for category_kr, category_en in category_map.items():
        if category_kr in category_list:
            # Current period data (as a line chart)
            traces.append({
                'x': chart_labels,
                'y': [data_by_year_month.get(p[0], {}).get(p[1], {}).get(category_en, 0) for p in all_periods],
                'name': f'선택기간({category_kr})',
                'type': 'scatter',
                'mode': 'lines+markers',
                'marker': {'color': colors[category_kr]},
            })
            # Previous year's data (as a bar chart)
            traces.append({
                'x': chart_labels,
                'y': [data_by_year_month.get(p[0] - 1, {}).get(p[1], {}).get(category_en, 0) for p in all_periods],
                'name': f'전년동기({category_kr})',
                'type': 'bar',
                'marker': {'color': bar_colors[category_kr]},
            })

    return {"tableData": table_data, "chartData": traces}

# bump chart data
def get_bump_chart_data(item_code: str, start_year: int, end_year: int, start_month: Optional[int] = None, end_month: Optional[int] = None):
    """
    Fetches and processes production data for all items to be used in a bump chart.
    The provided item_code is used to validate the request, but data for all items is fetched for ranking.
    """
    # Check if the provided item_code is valid
    item_to_highlight = item_crud.get_item_by_name(item_name=item_code)
    if not item_to_highlight:
        raise ValueError(f"Item with name {item_code} not found")

    sm = start_month if start_month is not None else 1
    em = end_month if end_month is not None else 12

    all_items = item_crud.get_items()
    item_name_map = {
        'Mackerel': '고등어',
        'CutlassFish': '갈치',
        'Calamari': '오징어',
    }
    all_item_names_kr = [item_name_map.get(item['item_name'], item['item_name']) for item in all_items]

    traces = []

    start_date = datetime(start_year, sm, 1)
    end_date = datetime(end_year, em, 1) + relativedelta(months=1)

    # Fetch all relevant data in a single, more efficient query
    with db_session() as cursor:
        sql = """
            SELECT
                i.item_name,
                EXTRACT(YEAR FROM ir.month_date) AS year,
                EXTRACT(MONTH FROM ir.month_date) AS month,
                SUM(ir.production) AS production
            FROM item_retail ir
            JOIN item i ON ir.item_pk = i.item_pk
            WHERE ir.month_date >= %s AND ir.month_date < %s
            GROUP BY i.item_name, year, month
            ORDER BY i.item_name, year, month
        """
        cursor.execute(sql, (start_date, end_date))
        all_results = cursor.fetchall()

    # Process data into a nested dictionary for easy access: {item_name: {period: production}}
    data_by_item_period = {}
    for row in all_results:
        item_name = row['item_name']
        period = f"{int(row['year'])}-{int(row['month']):02d}"
        if item_name not in data_by_item_period:
            data_by_item_period[item_name] = {}
        data_by_item_period[item_name][period] = row['production']

    # Generate all periods in the range for the x-axis
    labels = []
    current_date = start_date
    while current_date < end_date:
        labels.append(current_date.strftime('%Y-%m'))
        current_date += relativedelta(months=1)

    # Create a trace for each item
    for item in all_items:
        item_name_en = item['item_name']
        item_name_kr = item_name_map.get(item_name_en, item_name_en)

        # Map the production data to the full list of labels, filling missing months with 0
        production_data = [data_by_item_period.get(item_name_en, {}).get(label, 0) for label in labels]

        traces.append({
            'x': labels,
            'y': production_data,
            'name': f'{item_name_kr} (생산)',
            'type': 'line',
        })

    return {"chartData": traces, "categories": all_item_names_kr}