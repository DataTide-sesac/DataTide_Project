import PublicFunc as pf
import pandas as pd
from sqlalchemy import create_engine, text
func = pf.PublicFunc()

# 테이블 삭제
def DropTables():
    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    with engine.connect() as conn:
        print(f'Connected {user}')

        # 외래키 제약 제거
        conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))

        # 테이블 삭제
        conn.execute(text(f'''
                          DROP TABLE 
                          location,
                          item,
                          item_retail,
                          ground_weather,
                          sea_weather
                          '''))

# 테이블 생성
def CreateTables():
    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    with engine.connect() as conn:
        print(f'Connected {user}')

        # location
        conn.execute(text(f'''
                    create table location(
                    local_pk INT primary key AUTO_INCREMENT,
                    local_name varchar(30)
                );
                '''))
        
        # item
        conn.execute(text(f'''
                    CREATE TABLE item(
                    item_pk   INT PRIMARY key AUTO_INCREMENT,
                    item_name VARCHAR(20)
                );
                '''))
        
        # ground_weather
        conn.execute(text(f'''
                    create table ground_weather(
                    ground_pk BIGINT PRIMARY key AUTO_INCREMENT,
                    month_date date,
                    temperature float,
                    rain float
                );
                '''))
        
        # item_retail
        conn.execute(text(f'''
                    create table item_retail(
                    retail_pk BIGINT PRIMARY key AUTO_INCREMENT,
                    item_pk int,
                    month_date date,
                    production int,
                    inbound int,
                    sales int,
                    
                    FOREIGN KEY (item_pk) REFERENCES item(item_pk)
                );
                '''))
        
        # item_predict
        conn.execute(text(f'''
                    create table item_predict(
                    predict_pk BIGINT PRIMARY key AUTO_INCREMENT,
                    item_pk int,
                    month_date date,
                    production int,
                    inbound int,
                    sales int,
                    
                    FOREIGN KEY (item_pk) REFERENCES item(item_pk)
                );
                '''))
        
        # sea_weather
        conn.execute(text(f'''
                    create table sea_weather(
                    sea_pk bigint PRIMARY key AUTO_INCREMENT,
                    local_pk int,
                    month_date date,
                    temperature float,
                    wind float,
                    salinity float,
                    wave_height float,
                    wave_period float,
                    wave_speed float,
                    rain float,
                    snow float,
                    
                    FOREIGN KEY (local_pk) REFERENCES location(local_pk)
                );
                '''))

# ground_weather
def GroundWeatherAdd(filePath):
    itemDic = {
        '일시':'month_date',
        '평균기온':'temperature',
        '평균강수':'rain'
    }
    fileName=func.ReadFold(filePath)
    for file in fileName:
        df = func.ReadCSV(filePath, file)

    df.rename(columns=itemDic,inplace=True)

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    df.to_sql(name='ground_weather', con=engine, if_exists='append',index=False)

# sea_weather
def SeaWeatherAdd(filePath):
    itemDic = {
        '지역':'local_name',
        '일시':'month_date',
        '수온':'temperature',
        '염분':'salinity',
        '유속':'wave_speed',
        '유의파고':'wave_height',
        '유의파주기':'wave_period',
        '풍속':'wind',
        '강수량':'rain',
        '적설량':'snow'
    }
    fileName=func.ReadFold(filePath)
    for file in fileName:
        df = func.ReadCSV(filePath, file)

    df.rename(columns=itemDic,inplace=True)
    

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    # 부모테이블에서 키,이름 받기
    locationKey = pd.read_sql('SELECT local_pk, local_name FROM location', engine)

    # 데이터 합치기
    df_merged = pd.merge(df,locationKey, how='left', on='local_name')

    df_insert = df_merged[['local_pk','month_date','temperature','wind','salinity','wave_height','wave_period','wave_speed','rain','snow']]

    df_insert.to_sql(name='sea_weather', con=engine, if_exists='append', index=False)

# location
def LocationAdd(filePath):
    fileName=func.ReadFold(filePath)
    for file in fileName:
        df = func.ReadCSV(filePath, file)

    df.rename(columns={
        '지역':'local_name'
    },inplace=True)

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')
    
    df_localName = df['local_name'].drop_duplicates()
    df_localName.to_sql(name='location', con=engine, if_exists='append',index=False)

# item
def ItemAdd(filePath):
    itemDic = {
        '품목명':'item_name'
    }

    fileName = func.ReadFold(filePath)
    fishList = []
    for file in fileName:
        df = func.ReadCSV(filePath, file)
        df.reset_index(drop=True, inplace=True)
        
        fishList.append(df['품목명'])

    fishList = func.MixData(fishList)

    dfFishName = fishList.drop_duplicates()
    
    dfFishName.rename(columns=itemDic,inplace=True)

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    dfFishName.to_sql(name='item', con=engine, if_exists='append',index=False)

# item_retail
def RetailAdd(filePath):
    itemDic = {
        '품목명':'item_name',
        '날짜':'month_date',
        '생산':'production',
        '수입':'inbound',
        '판매':'sales'
        }
    
    fileName = func.ReadFold(filePath)
    fishList = []
    for file in fileName:
        df = func.ReadCSV(filePath, file)
        df.reset_index(drop=True, inplace=True)

        fishList.append(df)

    fishList = func.MixData(fishList)

    fishList.rename(columns=itemDic, inplace=True)

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    # 부모테이블에서 키,이름 받기
    itemKey = pd.read_sql('SELECT item_pk, item_name FROM item', engine)

    # 데이터 합치기
    dfMerged = pd.merge(fishList,itemKey, how='left', on='item_name')

    dfInsert = dfMerged[['item_pk','production','inbound','sales','month_date']]

    dfInsert.to_sql(name='item_retail', con=engine, if_exists='append',index=False)

if __name__ == '__main__':
    # 필요한 것만 주석 해제해서 쓰기
    filePath='./DataSet/Total'

    # DropTables()
    # CreateTables()

    GroundWeatherAdd(f'{filePath}/GroundWeather')
    # LocationAdd(f'{filePath}/SeaWeather')
    # SeaWeatherAdd(f'{filePath}/SeaWeather')
    # ItemAdd(f'{filePath}/FishData')
    # RetailAdd(f'{filePath}/FishData')


