from db.session import db_session
from typing import List

def get_fisheries_analysis_data(item_pk: int, years_to_query: List[int]):
    """
    Fetches and aggregates fisheries data from the database for analysis.
    """
    if not years_to_query:
        return []

    with db_session() as cursor:
        placeholders = ','.join(['%s'] * len(years_to_query))
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
        # The parameters must be a single tuple
        params = (item_pk,) + tuple(years_to_query)
        cursor.execute(sql, params)
        return cursor.fetchall()
