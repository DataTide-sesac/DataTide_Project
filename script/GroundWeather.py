import PublicFunc as pf
import pandas as pd

func = pf.PublicFunc()

def GroundWeather(filePath,saveFilePath):
    groundDic = {'속초':'강원','인천':'경기','영덕':'경북',
                 '부산':'부산','목포':'전남','부안':'전북',
                 '제주':'제주','서산':'충남','통영':'통영'}

    WeatherNameList = [
                    '150101_250827_전국_지형날씨.csv',
                    '150101_250827_통영_지형날씨.csv'
                    ]
    fileList = []
    for file in WeatherNameList:
        df = func.ReadCSV(filePath,file,encoding='cp949')
        fileList.append(df)
    fileList = func.MixData(fileList)
    fileList = fileList[~fileList['일시'].str.contains('2025-08')]
    fileList = fileList[['지점명','일시','평균기온','월합강수량','최심적설']]
    fileList['월합강수량'] = func.ChangeNull(fileList['월합강수량'],0)
    fileList['최심적설'] = func.ChangeNull(fileList['최심적설'],0)
    fileList['지점명'] = fileList['지점명'].replace(groundDic)
    fileList = func.AddLabels(fileList,['지역','일시','평균기온','평균강수','적설량'])

    func.SaveCSV(fileList,f'{saveFilePath}/kr_temp_percip.csv')

def AllGroundWeather(filePath,saveFilePath):

    fileNameWeather = '150101_250827_한국_기온.csv'
    fileNameRain = '150101_250827_한국_강수량.csv'

    df1 = func.ReadCSV(filePath,fileNameWeather,7,'cp949')
    df2 = func.ReadCSV(filePath,fileNameRain,7,'cp949')

    dfCut1 = df1[~df1['일시'].str.contains('2025-08',na=False)].sort_values(by='일시')
    dfCut2 = df2[~df2['일시'].str.contains('2025-08',na=False)].sort_values(by='일시')

    dfCut1 = dfCut1.loc[:,['일시','평균기온']]
    dfCut2 = dfCut2.loc[:,['일시','강수량']]

    func.SaveCSV(dfCut1,f'{saveFilePath}/전국_기온.csv')
    func.SaveCSV(dfCut2,f'{saveFilePath}/전국_강수.csv')

def AddHorizontal(filePath, saveFilePath):

    fileData = func.ReadFold(filePath)
    
    groundList = []
    for file in fileData:
        df = func.ReadCSV(filePath,file)
        df['일시'] = df['일시'].str.replace('\t','')

        # 이미 형식이 일치 할 시 안바꿈
        df['일시'] = df['일시'].apply(lambda x: str(x) + '-01' if len(str(x)) == 7 else x)
        
        groundList.append(df)


    df = func.MixData(groundList,1)
    
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.T.drop_duplicates().T

    df = func.AddLabels(df,['일시','평균기온','평균강수'])

    func.SaveCSV(df,f'{saveFilePath}/전국_기온_강수.csv')

if __name__ == '__main__':
    #Path는 따로 지정해 줄 것
    #함수 내에도 하드코딩 되어있는 Path 있을 수 있음 ###

    filePath = './data/ground_weather'
    saveFilePath = '.'
    # AllGroundWeather(filePath,saveFilePath)
    # AllGroundWeatherTotal()
    filePath = './testDataFold/GroundWeather'
    AddHorizontal(filePath,saveFilePath)
    pass