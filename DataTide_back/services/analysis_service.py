# services/analysis_service.py
from DataTide_back.db.session import db_session
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
        return cursor.fetchall()

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
            current_period_name = f'{start_year}~{end_year}' if start_year != end_year else str(start_year)
            prev_period_name = f'{start_year - 1}~{end_year - 1}' if start_year != end_year else str(start_year - 1)

            # DEBUG: Print the generated trace name
            print(f"Generated trace name: {current_period_name}({category_kr})")

            traces.append({
                'x': chart_labels,
                'y': [data_by_year_month.get(p[0], {}).get(p[1], {}).get(category_en, 0) for p in all_periods],
                'name': f'{current_period_name}({category_kr})',
                'type': 'scatter',
                'mode': 'lines+markers',
                'marker': {'color': colors[category_kr]},
            })
            traces.append({
                'x': chart_labels,
                'y': [data_by_year_month.get(p[0] - 1, {}).get(p[1], {}).get(category_en, 0) for p in all_periods],
                'name': f'{prev_period_name}({category_kr})',
                'type': 'bar',
                'marker': {'color': bar_colors[category_kr]},
            })

    return {"tableData": table_data, "chartData": traces}

def get_prediction_data(item_names: List[str], location_name: str, base_date: str):
    # This is a placeholder implementation
    # In a real application, you would fetch data from a database
    # and run a prediction model.
    print(f"Fetching prediction data for items: {item_names}, location: {location_name}, base_date: {base_date}")

    # Dummy data for demonstration
    dummy_data = {
        "labels": ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01"],
        "datasets": [
            {
                "label": item_name,
                "data": [100, 120, 110, 130, 125, 140],
                "borderColor": f"rgb({i*50}, {255-i*50}, {i*100})",
                "backgroundColor": f"rgba({i*50}, {255-i*50}, {i*100}, 0.5)",
            } for i, item_name in enumerate(item_names)
        ]
    }
    return dummy_data

def get_stats_data(item_names: List[str], start_year: int, end_year: int, location_name: str):
    # This is a placeholder implementation
    # In a real application, you would fetch and process statistical data.
    print(f"Fetching stats data for items: {item_names}, start: {start_year}, end: {end_year}, location: {location_name}")

    # Dummy data for demonstration
    dummy_data = {
        "labels": [str(year) for year in range(start_year, end_year + 1)],
        "datasets": [
            {
                "label": item_name,
                "data": [1000, 1200, 1100, 1300, 1250, 1400][:end_year - start_year + 1],
                "borderColor": f"rgb({i*50}, {255-i*50}, {i*100})",
                "backgroundColor": f"rgba({i*50}, {255-i*50}, {i*100}, 0.5)",
            } for i, item_name in enumerate(item_names)
        ]
    }
    return dummy_data

def create_prediction_excel(item_names: List[str], location_name: str, base_date: str):
    # This is a placeholder implementation
    print(f"Creating prediction excel for items: {item_names}, location: {location_name}, base_date: {base_date}")
    
    # Dummy data for demonstration
    df = pd.DataFrame({
        "Date": ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01"],
        item_names[0]: [100, 120, 110, 130, 125, 140]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Prediction')
    
    filename = f"prediction_{'_'.join(item_names)}_{base_date}.xlsx"
    output.seek(0)
    return output, filename

def create_stats_excel(item_names: List[str], location_name: str, start_year: int, end_year: int):
    # This is a placeholder implementation
    print(f"Creating stats excel for items: {item_names}, start: {start_year}, end: {end_year}, location: {location_name}")

    # Dummy data for demonstration
    df = pd.DataFrame({
        "Year": [str(year) for year in range(start_year, end_year + 1)],
        item_names[0]: [1000, 1200, 1100, 1300, 1250, 1400][:end_year - start_year + 1]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Statistics')

    filename = f"stats_{'_'.join(item_names)}_{start_year}_{end_year}.xlsx"
    output.seek(0)
    return output, filename

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
        return cursor.fetchall()

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

def get_prediction_data(item_names: List[str], location_name: str, base_date: str):
    # This is a placeholder implementation
    # In a real application, you would fetch data from a database
    # and run a prediction model.
    print(f"Fetching prediction data for items: {item_names}, location: {location_name}, base_date: {base_date}")

    # Dummy data for demonstration
    dummy_data = {
        "labels": ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01"],
        "datasets": [
            {
                "label": item_name,
                "data": [100, 120, 110, 130, 125, 140],
                "borderColor": f"rgb({i*50}, {255-i*50}, {i*100})",
                "backgroundColor": f"rgba({i*50}, {255-i*50}, {i*100}, 0.5)",
            } for i, item_name in enumerate(item_names)
        ]
    }
    return dummy_data

def get_stats_data(item_names: List[str], start_year: int, end_year: int, location_name: str):
    # This is a placeholder implementation
    # In a real application, you would fetch and process statistical data.
    print(f"Fetching stats data for items: {item_names}, start: {start_year}, end: {end_year}, location: {location_name}")

    # Dummy data for demonstration
    dummy_data = {
        "labels": [str(year) for year in range(start_year, end_year + 1)],
        "datasets": [
            {
                "label": item_name,
                "data": [1000, 1200, 1100, 1300, 1250, 1400][:end_year - start_year + 1],
                "borderColor": f"rgb({i*50}, {255-i*50}, {i*100})",
                "backgroundColor": f"rgba({i*50}, {255-i*50}, {i*100}, 0.5)",
            } for i, item_name in enumerate(item_names)
        ]
    }
    return dummy_data

def create_prediction_excel(item_names: List[str], location_name: str, base_date: str):
    # This is a placeholder implementation
    print(f"Creating prediction excel for items: {item_names}, location: {location_name}, base_date: {base_date}")
    
    # Dummy data for demonstration
    df = pd.DataFrame({
        "Date": ["2025-08", "2025-09", "2025-10", "2025-11", "2025-12", "2026-01"],
        item_names[0]: [100, 120, 110, 130, 125, 140]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Prediction')
    
    filename = f"prediction_{'_'.join(item_names)}_{base_date}.xlsx"
    output.seek(0)
    return output, filename

def create_stats_excel(item_names: List[str], location_name: str, start_year: int, end_year: int):
    # This is a placeholder implementation
    print(f"Creating stats excel for items: {item_names}, start: {start_year}, end: {end_year}, location: {location_name}")

    # Dummy data for demonstration
    df = pd.DataFrame({
        "Year": [str(year) for year in range(start_year, end_year + 1)],
        item_names[0]: [1000, 1200, 1100, 1300, 1250, 1400][:end_year - start_year + 1]
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Statistics')

    filename = f"stats_{'_'.join(item_names)}_{start_year}_{end_year}.xlsx"
    output.seek(0)
    return output, filename