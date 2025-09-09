# test/clear_db.py
import pandas as pd
from sqlalchemy import create_engine, text

def clear_tables():
    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    tables_to_clear = [
        'item_retail',
        'item',
        'sea_weather',
        'location',
        'ground_weather'
    ]
    
    with engine.connect() as connection:
        # SET FOREIGN_KEY_CHECKS = 0;
        connection.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))
        print("Disabled foreign key checks.")

        for table in tables_to_clear:
            try:
                print(f"Clearing table: {table}...")
                # Use TRUNCATE TABLE for faster deletion
                connection.execute(text(f'TRUNCATE TABLE {table};'))
                print(f"Successfully cleared table: {table}")
            except Exception as e:
                print(f"Error clearing table {table}: {e}")
        
        # SET FOREIGN_KEY_CHECKS = 1;
        connection.execute(text('SET FOREIGN_KEY_CHECKS = 1;'))
        print("Enabled foreign key checks.")
        
        # Commit the changes
        connection.commit()


if __name__ == '__main__':
    print("Starting to clear database tables...")
    clear_tables()
    print("Finished clearing database tables.")
