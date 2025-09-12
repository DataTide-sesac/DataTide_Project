import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import IntegrityError # 추가: ORM 예외 처리 위해
import os
from datetime import datetime

# 프로젝트 루트 설정
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'database.db')
DATASET_PATH = os.path.join(PROJECT_ROOT, 'DataSet', 'Total', 'FishData')
DB_URL = f'sqlite:///{DATABASE_PATH}'

Base = declarative_base() # 최신 위치로 수정

class Item(Base):
    __tablename__ = 'item'
    item_pk = Column(Integer, primary_key=True)
    item_name = Column(String)

class ItemRetail(Base):
    __tablename__ = 'item_retail'
    retail_pk = Column(Integer, primary_key=True, autoincrement=True)
    item_pk = Column(Integer, ForeignKey('item.item_pk'))
    month_date = Column(DateTime)
    production = Column(Integer)
    inbound = Column(Integer)
    sales = Column(Integer)

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

def load_fish_data():
    print("Loading fish data (item and item_retail) into DB...")

    # --- Load Item Data ---
    item_names = set()
    for fish_type in ['Calamari', 'CutlassFish', 'Mackerel']:
        file_path = os.path.join(DATASET_PATH, f'{fish_type}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            item_names.update(df['품목명'].unique())
        else:
            print(f"Warning: {file_path} not found.")

    if item_names:
        items_df = pd.DataFrame({'item_name': list(item_names)})
        items_df.to_sql('item', con=engine, if_exists='append', index=False)
        print(f"Inserted {len(item_names)} unique items into 'item' table.")
    else:
        print("No unique items found to insert.")

    # --- Load Item Retail Data ---
    item_pk_map_df = pd.read_sql('SELECT item_pk, item_name FROM item', con=engine)
    item_pk_map = item_pk_map_df.set_index('item_name')['item_pk'].to_dict()

    all_retail_data = []
    for fish_type in ['Calamari', 'CutlassFish', 'Mackerel']:
        file_path = os.path.join(DATASET_PATH, f'{fish_type}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df.rename(columns={
                '품목명': 'item_name',
                '날짜': 'month_date',
                '생산': 'production',
                '수입': 'inbound',
                '판매': 'sales'
            }, inplace=True)

            df['item_pk'] = df['item_name'].map(item_pk_map)
            df['month_date'] = pd.to_datetime(df['month_date'])
            df_insert = df[['item_pk', 'month_date', 'production', 'inbound', 'sales']]
            all_retail_data.append(df_insert)
        else:
            print(f"Warning: {fish_type}.csv not found.")

    if len(all_retail_data) > 0:
        final_retail_df = pd.concat(all_retail_data, ignore_index=True)

        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            retail_records = [
                ItemRetail(
                    item_pk=row['item_pk'],
                    month_date=row['month_date'],
                    production=row['production'],
                    inbound=row['inbound'],
                    sales=row['sales']
                ) for _, row in final_retail_df.iterrows()
            ]

            session.add_all(retail_records)
            session.commit()
            print(f"Inserted {len(retail_records)} records into 'item_retail' table.")

        except IntegrityError as e: # SQLAlchemy 예외 처리 추가
            session.rollback()
            print(f"데이터 삽입 중 무결성 제약조건 오류 발생: {e}")
        except Exception as e: # 일반적인 예외 처리
            session.rollback()
            print(f"데이터 삽입 중 일반 오류 발생: {e}")
        finally:
            session.close()

    else:
        print("No retail data found to insert.")

    print("Data loading complete.")


if __name__ == "__main__":
    # 초기 실행에서 테이블이 없을 경우 생성 (파일 존재 여부 확인)
    if not os.path.exists(DATABASE_PATH):
        Base.metadata.create_all(engine)
        print("테이블이 새로 생성되었습니다.")

    load_fish_data()
    