import PublicFunc as pf
func = pf.PublicFunc()

def SeaWeather(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    savePath = f'{filePath}'
    for local in localList:
        seaWeatherList = []
        fileName = func.ReadFold(filePath)
        for file in fileName:
            if local in file:
                df = func.ReadCSV(filePath,file)
                df.reset_index(drop=True, inplace=True)
                seaWeatherList.append(df)
        df = func.MixData(seaWeatherList)

        func.SaveCSV(df,f'{savePath}/{local}_SeaWeather.csv')
        
def GroundWeather(filePath):
    groundList = []
    fileName = func.ReadFold(filePath)
    for file in fileName:
        df = func.ReadCSV(f'{filePath}',f'{file}',encoding='cp949')
        groundList.append(df)

    df = func.MixData(groundList)

    
    print(df['일시'])

    dfCut = df[~df['일시'].str.contains('2025-08')]
    print(dfCut)

    dfCut['월합강수량'] = func.ChangeNull(dfCut['월합강수량'],0)
    dfCut['최심적설'] = func.ChangeNull(dfCut['최심적설'],0)

    # dfCut = df[~df['일시'].str.contains('08')]
    cityList = ['속초','인천','서산','부산','목포','제주','부안','영덕','통영']
    print(dfCut)
    for city in cityList:
        dfCityCut = dfCut[dfCut['지점명'].str.contains(city)]

        dfCityCut = dfCityCut[['지점명','일시','월합강수량','최심적설']]

        func.SaveCSV(dfCityCut,f'{filePath}/{city}_날씨.csv')

# 복원중    
# def SeaWeatherRainSnow(filePath):

def SeaWeatherTotal(filePath):
    fileName = func.ReadFold(filePath)
    saveFilePath = './DataSet/Total/SeaWeather'
    SeaWeatherList = []
    for file in fileName:
        df = func.ReadCSV(f'{filePath}',f'{file}')
        SeaWeatherList.append(df)

    df = func.MixData(SeaWeatherList)

    # 중복제거
    df = df.loc[:, ~df.columns.duplicated()]

    func.SaveCSV(df,f'{saveFilePath}/SeaWeatherTotal.csv')


if __name__ == '__main__':
    filePath = './DataSet'
    # SeaWeather(f'{filePath}/SeaWeather')
    # GroundWeather(f'{filePath}/GroundWeather')
    # SeaWeatherTotal(f'{filePath}/SeaWeather')
    pass