
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DataTide_back.db.session import db_session

def check_item_predict_data():
    """Fetches a few rows from the item_predict table to verify its content."""
    with db_session() as cursor:
        sql = """
            SELECT *
            FROM item_predict
            LIMIT 10
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        if results:
            print("Sample data from item_predict table:")
            for row in results:
                print(row)
        else:
            print("No data found in item_predict table.")

if __name__ == "__main__":
    check_item_predict_data()
