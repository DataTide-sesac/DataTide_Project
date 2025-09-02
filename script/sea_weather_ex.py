import PublicFunc as pf
func = pf.PublicFunc()

filePath = './data/sample/통영/2025_월간보고서/수온'
# foldData = func.ReadFold('./data/sample/통영/sea_weather_ex/2025_월간보고서/수온')

# print(foldData)
def TestDataSave():
    regionType = ['강원','경기','경북','부산_울산','전남_목포','전북','제주','충남','통영']
    selectType = ['수온','염분','유속','유의파고','유의파주기','풍속']
    tempList = []
    for region in regionType:
        for foldSelect in selectType:
            tempList = []
            selectFilePath = f'./data/sample/{region}/2025_월간보고서/{foldSelect}'
            print("*"*10)
            print(selectFilePath)
            print("*"*10)
            foldData = func.ReadFold(selectFilePath)
            for item in foldData:
                tempData = func.ReadPDF(selectFilePath, item)
                tempList.append(tempData)
            df = func.MixData(tempList)
            labels = ['']*26
            labels[24] = '평균'
            func.AddLabels(df,labels)

            func.SaveCSV(df,f'testWeather_{2025}_{region}_{foldSelect}.csv')

def TestAvgSave():
    regionType = ['강원','경기','경북','부산_울산','전남_목포','전북','제주','충남','통영']
    selectType = ['수온','염분','유속','유의파고','유의파주기','풍속']
    filePath = f'./testData/전처리_전'
    # fileName = f'testWeather_2025_강원_수온.csv'
    fileData = func.ReadFold(filePath)
    for item in fileData:
        testCSV = func.ReadCSV(filePath,item)
        testCSV = testCSV['평균']

        func.SaveCSV(testCSV,item)

def InsertCol():
    regionType = ['강원','경기','경북','부산_울산','전남_목포','전북','제주','충남','통영']
    selectType = ['수온','염분','유속','유의파고','유의파주기','풍속']
    filePath = f'./testData'
    fileData = func.ReadFold(filePath)
    for item in fileData:
        testCSV = func.ReadCSV(filePath,item)
        if '강원' in item:
            testCSV.insert(0,'지역','강원')
        elif '경기' in item:
            testCSV.insert(0,'지역','경기')
        elif '경북' in item:
            testCSV.insert(0,'지역','경북')
        elif '부산_울산' in item:
            testCSV.insert(0,'지역','부산_울산')
        elif '전남_목포' in item:
            testCSV.insert(0,'지역','전남_목포')
        elif '전북' in item:
            testCSV.insert(0,'지역','전북')
        elif '제주' in item:
            testCSV.insert(0,'지역','제주')
        elif '충남' in item:
            testCSV.insert(0,'지역','충남')
        elif '통영' in item:
            testCSV.insert(0,'지역','통영')
        testCSV.insert(1,'일시',['2025-01-01','2025-02-01','2025-03-01','2025-04-01','2025-05-01','2025-06-01','2025-07-01'])
        func.SaveCSV(testCSV,item)

def AddCol():
    filePath = f'./testData'
    fileData = func.ReadFold(filePath)
    tempList_1 = []
    tempList_2 = []
    tempList_3 = []
    tempList_4 = []
    tempList_5 = []
    tempList_6 = []

    groundDic = {'속초':'강원','인천':'경기','영덕':'경북',
                 '부산_울산':'부산','전남_목포':'전남','부안':'전북',
                 '제주':'제주','서산':'충남','통영':'통영'}

    for item in fileData:
        temp = func.ReadCSV(filePath,item)
        temp['지역'] = temp['지역'].replace(groundDic)
        if '수온' in item:
            tempList_1.append(temp)
            df_1 = func.MixData(tempList_1)
        elif '염분' in item:
            tempList_2.append(temp)
            df_2 = func.MixData(tempList_2)
        elif '유속' in item:
            tempList_3.append(temp)
            df_3 = func.MixData(tempList_3)
        elif '유의파고' in item:
            tempList_4.append(temp)
            df_4 = func.MixData(tempList_4)
        elif '유의파주기' in item:
            tempList_5.append(temp)
            df_5 = func.MixData(tempList_5)
        elif '풍속' in item:
            tempList_6.append(temp)
            df_6 = func.MixData(tempList_6)

    func.SaveCSV(df_1,'MixWeather_수온.csv')
    func.SaveCSV(df_2,'MixWeather_염분.csv')
    func.SaveCSV(df_3,'MixWeather_유속.csv')
    func.SaveCSV(df_4,'MixWeather_유의파고.csv')
    func.SaveCSV(df_5,'MixWeather_유의파주기.csv')
    func.SaveCSV(df_6,'MixWeather_풍속.csv')

def AddColWeather():
    groundDic = {'속초':'강원','인천':'경기','영덕':'경북',
                 '울산':'부산','목포':'전남','부안':'전북',
                 '제주':'제주','서산':'충남','통영':'통영'}
    filePath = f'./testData/전처리_후/날씨'
    fileData = func.ReadFold(filePath)
    tempList = []
    for item in fileData:
        temp = func.ReadCSV(filePath,item)
        temp['지점명'] = temp['지점명'].replace(groundDic)
        tempList.append(temp)
    df = func.MixData(tempList)
    func.SaveCSV(df,'전국_강수량_적설량.csv')

def AddColHorizontal():
    filePath = f'./testData'

    fileData = func.ReadFold(filePath)
    
    tempList = []
    for item in fileData:
        temp = func.ReadCSV(filePath,item)
        tempList.append(temp)

    df = func.MixData(tempList,1)
    
    df = df.loc[:, ~df.columns.duplicated()]
    df = df.T.drop_duplicates().T
    df = func.AddLabels(df,['지역','일시','수온','염분','유속','유의파고','유의파주기','풍속','강수량','적설량'])


    func.SaveCSV(df,'테스트1111.csv')


if __name__ == "__main__":
    # TestAvgSave()
    # InsertCol()
    # AddCol()
    # AddColWeather()
    AddColHorizontal()