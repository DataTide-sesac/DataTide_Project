import PublicFunc as pf
import pandas as pd

func = pf.PublicFunc()

#데이터 추출
def SeaData(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    yearList = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
    typeList = ['수온','염분','유속','유의파고','유의파주기','풍속']

    for local in localList:
        for year in yearList:
            for type in typeList:
                fileName = func.ReadFold(f'{filePath}/{local}/{year}_월간보고서/{type}')
                fileList = []
                for file in fileName:
                    if '월간' in file:
                        df = func.ReadPDF(f'{filePath}/{local}/{year}_월간보고서/{type}',file)
                        fileList.append(df)
                    elif '년간' in file:
                        df = func.ReadPDF(f'{filePath}/{local}/{year}_월간보고서/{type}',file,'year')
                        df = df.T['평균']
                if '월간' in file:
                    fileList = func.MixData(fileList)
                    labelList = [None] * 26
                    labelList[24] = '평균'
                    fileList = func.AddLabels(fileList,labelList)
                    fileList = fileList['평균']
                    func.SaveCSV(fileList, f'./testDataFold/{local}/{year}_월간보고서/{local}_{year}_{type}.csv')
                elif '년간' in file:
                    func.SaveCSV(df, f'./testDataFold/{local}/{year}_월간보고서/{local}_{year}_{type}.csv')

#NaN값 확인
def IsNullCheck(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    yearList = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
    for local in localList:
        for year in yearList:
            fileName = func.ReadFold(f'{filePath}/{local}/{year}_월간보고서')
            noneList = []
            for file in fileName:
                df = func.ReadCSV(f'{filePath}/{local}/{year}_월간보고서',file)
                if df.isnull().values.any():
                    noneList.append(f'{filePath}, {file}')
            
            for values in noneList:
                print(values)

#컬럼 갯수 체크         
def IsColumnsCheck(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    yearList = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']

    for local in localList:
        for year in yearList:
            fileName = func.ReadFold(f'{filePath}/{local}/{year}_월간보고서')
            
            nullColumnsList = []
            for file in fileName:
                df = func.ReadCSV(f'{filePath}/{local}/{year}_월간보고서',file)
                if (year != '2025' and df.shape[0] != 12) or (year == '2025' and df.shape[0] != 7) :
                    nullColumnsList.append(f'{filePath}, {file}')
            
            for values in nullColumnsList:
                print(values)

#지역,날짜 삽입
def SeaWeatherAddColumns(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    yearList = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
    monthList = ['01','02','03','04','05','06','07','08','09','10','11','12']
    typeList = ['지역','일시','수온','염분','유속','유의파고','유의파주기','풍속']

    for local in localList:
        for year in yearList:
            fileList = []
            fileName = func.ReadFold(f'{filePath}/{local}/{year}_월간보고서')
            for file in fileName:
                df = func.ReadCSV(f'{filePath}/{local}/{year}_월간보고서',file)
                func.AddColumns(df,0,'지역',local)
                #날짜 삽입 / df의 행 갯수까지
                func.AddColumns(df,1,'일시',[f"{year}-{month}-01" for month in monthList[:len(df)]])
                df = df.reset_index(drop=True)
                fileList.append(df)
                
            fileList = func.MixData(fileList,1)
            fileList = fileList.T.drop_duplicates().T
            fileList = func.AddLabels(fileList,typeList)
            func.SaveCSV(fileList,f'{filePath}/{local}_{year}_SeaWeather.csv')

#모든 연도 합치기
def MixAllData(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    for local in localList:
        fileName = func.ReadFold(filePath)
        fileList = []
        for file in fileName:
            if local in file:
                df = func.ReadCSV(f'{filePath}',file)
                fileList.append(df)
        fileList = func.MixData(fileList)
        func.SaveCSV(fileList,f'{filePath}/{local}_SeaWeather.csv')

#강수량, 적설량 추가
def MergeRainSnow(filePath):
    groundFilePath = f'{filePath}/GroundWeather'
    groundFileName = 'kr_temp_percip.csv'
    
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    typeList = ['지역','일시','수온','염분','유속','유의파고','유의파주기','풍속','강수량','적설량']

    fileName = func.ReadFold(filePath)
    for local in localList:
        fileList = []
        dfGround = func.ReadCSV(groundFilePath,groundFileName)
        dfGround = dfGround[dfGround['지역'] == local]
        dfGround = dfGround[['평균강수','적설량']]
        for file in fileName:
            df = func.ReadCSV(filePath,file)
            if local in file:
                df = df.reset_index(drop=True)
                fileList.append(df)
                dfGround = dfGround.reset_index(drop=True)
                fileList.append(dfGround)
                break
        fileList = func.MixData(fileList,1)
        print(fileList)
        fileList = func.AddLabels(fileList,typeList)
    
    fileName = func.ReadFold(f'{filePath}/Sea')
    fileList = []
    for file in fileName:
        df = func.ReadCSV(f'{filePath}/Sea',file)
        fileList.append(df)
    fileList = func.MixData(fileList)

    func.SaveCSV(fileList,f'{filePath}/Total/SeaWeather/SeaWeatherTotal.csv')

if __name__ == '__main__':
    #함수 호출할 때 filePath랑 매개변수 바꿔 줄 것
    #함수 내에도 하드코딩 되어있는 Path 있으니 확인 필수 ###

    filePath = './data/sea_weather_data'
    # SeaData(filePath)
    filePath = './DataSet'
    # IsNullCheck(f'{filePath}/SeaWeather/Creck')
    # IsColumnsCheck(f'{filePath}/SeaWeather/Creck')
    # SeaWeatherAddColumns(f'{filePath}/SeaWeather')
    # MixAllData(f'{filePath}/SeaWather')
    #MergeRainSnow(filePath)
    pass
