"""주요 내용 및 변수명 점검
CSV 파일을 읽어들여 pandas DataFrame으로 변환 후, 한글 컬럼명을 프로젝트 변수명(item_name, month_date, production, inbound, sales 등)으로 정확히 변경하고 있습니다.
각 데이터 전처리 및 to_sql 메서드를 이용한 DB 테이블(ground_weather, sea_weather, location, item, item_retail)에 데이터 삽입 과정이 명확하고 체계적입니다.
특히 RetailAdd 함수에서 item 테이블과 item_retail 테이블 사이의 FK 역할을 하는 item_pk 키를 pd.merge로 잘 매핑하고 있어 DB 관계성 유지가 적절합니다.
DB 접속 정보는 하드코딩되어 있으니, 추후 환경변수나 설정파일로 분리하는 것이 좋겠습니다.
o 추후 CSV 파일명과 경로를 하드코딩하지 말고 인자로 받거나 설정파일에서 관리
o 예외 처리 부분을 보다 세밀하게 보완해 데이터 이상 상황 대비
o DB 접속 정보(특히 비밀번호)를 안전하게 환경변수 또는 비밀 정보 관리 시스템으로 전환
"""
#test/DBAdd.py
from pathlib import Path
import PublicFunc as pf
import pandas as pd
from sqlalchemy import create_engine
func = pf.PublicFunc()
#ground_weather
def GroundWeatherAdd(filePath):
    fileName='kr_temp_percip.csv'

    df = func.ReadCSV(filePath, fileName)

    df.rename(columns={
        '일시':'month_date',
        '평균기온':'temperature',
        '평균강수':'rain'
    },inplace=True)

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    df.to_sql(name='ground_weather', con=engine, if_exists='append',index=False)

def SeaWeatherAdd(filePath):
    fileName='SeaWeather_2025.csv'

    df = func.ReadCSV(filePath, fileName)

    df.rename(columns={
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
    },inplace=True)
    

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    #부모테이블에서 키,이름 받기
    locationKey = pd.read_sql('SELECT local_pk, local_name FROM location', engine)

    #데이터 합치기
    df_merged = pd.merge(df,locationKey, how='left', on='local_name')

    df_insert = df_merged[['local_pk','month_date','temperature','wind','salinity','wave_height','wave_period','wave_speed','rain','snow']]

    df_insert.to_sql(name='sea_weather', con=engine, if_exists='append', index=False)

def LocationAdd(filePath):
    fileName='SeaWeather_2025.csv'

    df = func.ReadCSV(filePath, fileName)

    df.rename(columns={
        '지역':'local_name'
    },inplace=True)

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')
    
    df_localName = df['local_name'].drop_duplicates().to_frame()
    df_localName.to_sql(name='location', con=engine, if_exists='append',index=False)


def ItemAdd(filePath):
    fileNameCalamari='Calamari_2025.csv'
    fileNameCutlassFish='CutlassFish_2025.csv'
    fileNameMackerel='Mackerel_2025.csv'

    dfCalamari = func.ReadCSV(filePath, fileNameCalamari)
    dfCutlassFish = func.ReadCSV(filePath, fileNameCutlassFish)
    dfMackerel = func.ReadCSV(filePath, fileNameMackerel)

    tempList = []
    tempList.append(dfCalamari['품목명'])
    tempList.append(dfCutlassFish['품목명'])
    tempList.append(dfMackerel['품목명'])

    tempList = func.MixData(tempList)

    dfFishName = tempList.drop_duplicates()
    
    dfFishName = dfFishName.rename(columns={
        '품목명':'item_name'
    })

    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    dfFishName.to_sql(name='item', con=engine, if_exists='append',index=False)

def RetailAdd(filePath):
    fileNameCalamari='Calamari_2025.csv'
    fileNameCutlassFish='CutlassFish_2025.csv'
    fileNameMackerel='Mackerel_2025.csv'

    dfCalamari = func.ReadCSV(filePath, fileNameCalamari)
    dfCutlassFish = func.ReadCSV(filePath, fileNameCutlassFish)
    dfMackerel = func.ReadCSV(filePath, fileNameMackerel)
    
    itemDic = {
        '품목명':'item_name',
        '날짜':'month_date',
        '생산':'production',
        '수입':'inbound',
        '판매':'sales'
        }
    
    
    if dfCalamari is not None:
        dfCalamari.rename(columns=itemDic, inplace=True)
    else:
        raise ValueError(f"Failed to read {fileNameCalamari}")

    if dfCutlassFish is not None:
        dfCutlassFish.rename(columns=itemDic, inplace=True)
    else:
        raise ValueError(f"Failed to read {fileNameCutlassFish}")

    if dfMackerel is not None:
        dfMackerel.rename(columns=itemDic, inplace=True)
    else:
        raise ValueError(f"Failed to read {fileNameMackerel}")



    user = 'team_dt'
    password = 'dt_1234'
    host = 'localhost'
    port = 3306
    database = 'datatide_db'

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')

    #부모테이블에서 키,이름 받기
    itemKey = pd.read_sql('SELECT item_pk, item_name FROM item', engine)
    
    #데이터 합치기
    dfMergedCalamari = pd.merge(dfCalamari,itemKey, how='left', on='item_name')
    dfMergedCutlassFish = pd.merge(dfCutlassFish,itemKey, how='left', on='item_name')
    dfMergedMackerel = pd.merge(dfMackerel,itemKey, how='left', on='item_name')

    dfInsertCalamari = dfMergedCalamari[['item_pk','production','inbound','sales','month_date']]
    dfInsertCutlassFish = dfMergedCutlassFish[['item_pk','production','inbound','sales','month_date']]
    dfInsertMackerel = dfMergedMackerel[['item_pk','production','inbound','sales','month_date']]

    dfInsertCalamari.to_sql(name='item_retail', con=engine, if_exists='append',index=False)
    dfInsertCutlassFish.to_sql(name='item_retail', con=engine, if_exists='append',index=False)
    dfInsertMackerel.to_sql(name='item_retail', con=engine, if_exists='append',index=False)




if __name__ == '__main__':
    #완성본 아님
    #fileName은 하드코딩 되어있음. 나중에 수정해야됨
    #아직 테스트 용도
    # Use pathlib to create a robust, absolute path
    filePath = Path(__file__).parent / 'data' / '테스트_완성'
    GroundWeatherAdd(filePath)
    LocationAdd(filePath)
    SeaWeatherAdd(filePath)
    ItemAdd(filePath)
    RetailAdd(filePath)
