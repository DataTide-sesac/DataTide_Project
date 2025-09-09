import PublicFunc as pf
func = pf.PublicFunc()

filePath = './data/ground_weather'

groundList = ['150101_250827_전국_지형날씨.csv',
              '150101_250827_통영_지형날씨.csv']
tempList = []
for item in groundList:
    groundWeather = func.ReadCSV(filePath, item, encoding='cp949')

    tempList.append(groundWeather)

df = func.MixData(tempList)

# print(df['일시'],df['월합강수량'],df['최심적설'])
# df['일시'] = df['일시'].str[:4]
print(df['일시'])
# df[df['일시']=='2025']
# dfCut = df[df['일시'].str.contains('2025')]
dfCut = df[df['일시'].str.contains('2025')&
           ~df['일시'].str.contains('08')]
print(dfCut)

dfCut['월합강수량'] = func.ChangeNull(dfCut['월합강수량'],0)
dfCut['최심적설'] = func.ChangeNull(dfCut['최심적설'],0)

# dfCut = df[~df['일시'].str.contains('08')]
cityList = ['속초','인천','서산','부산','목포','제주','부안','영덕','통영']
print(dfCut)
for city in cityList:
    dfCityCut = dfCut[dfCut['지점명'].str.contains(city)]
    # dfCityCut['월합강수량'] = func.ChangeNull(dfCityCut['월합강수량'],0)
    # dfCityCut['최심적설'] = func.ChangeNull(dfCityCut['최심적설'],0)

    dfCityCut = dfCityCut[['지점명','일시','월합강수량','최심적설']]

    func.SaveCSV(dfCityCut,f'{city}_날씨.csv')
# func.SaveCSV(dfCut,'전국날씨.csv')
