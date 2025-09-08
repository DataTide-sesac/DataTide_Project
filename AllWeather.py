import PublicFunc as pf
func = pf.PublicFunc()

def ReadCSVWeather():
    filePath = './data/ground_weather'

    fileNameWeather = '150101_250827_한국_기온.csv'
    fileNameRain = '150101_250827_한국_강수량.csv'

    df1 = func.ReadCSV(filePath,fileNameWeather,11,'cp949')
    df2 = func.ReadCSV(filePath,fileNameRain,12,'cp949')

    print("**"*15)
    print(df1)
    print("**"*15)
    print(df2)
    print("**"*15)
    dfCut1 = df1[df1['일시'].str.contains('2025',na=False)&
            ~df1['일시'].str.contains('08',na=False)].sort_values(by='일시')
    dfCut2 = df2[df2['일시'].str.contains('2025',na=False)&
            ~df2['일시'].str.contains('08',na=False)].sort_values(by='일시')

    dfCut1 = dfCut1.loc[:,['일시','평균기온']]
    dfCut2 = dfCut2.loc[:,['일시','평균월강수량']]


    print("**"*15)
    print(dfCut1)
    print("**"*15)
    print(dfCut2)
    print("**"*15)

    func.SaveCSV(dfCut1,'전국_기온.csv')
    func.SaveCSV(dfCut2,'전국_강수.csv')

def AddHorizontal():
    filePath = f'./testData'

    fileData = func.ReadFold(filePath)
    
    tempList = []
    for item in fileData:
        temp = func.ReadCSV(filePath,item)
        tempList.append(temp)

    df = func.MixData(tempList,1)
    
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.T.drop_duplicates().T

    df = func.AddLabels(df,['일시','평균기온','평균강수'])

    func.SaveCSV(df,'전국_기온_강수.csv')


if __name__ == '__main__':
    AddHorizontal()