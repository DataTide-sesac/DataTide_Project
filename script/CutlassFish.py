import PublicFunc as pf
import pandas as pd

filePath = './data/fish/Cutlassfish'
fileName = ['Cutlassfish_201501_201508.xlsx',
            'Cutlassfish_201509_201608.xlsx',
            'Cutlassfish_201609_201708.xlsx',
            'Cutlassfish_201709_201808.xlsx',
            'Cutlassfish_201809_201908.xlsx',
            'Cutlassfish_201909_202008.xlsx',
            'Cutlassfish_202009_202108.xlsx',
            'Cutlassfish_202109_202208.xlsx',
            'Cutlassfish_202209_202308.xlsx',
            'Cutlassfish_202309_202408.xlsx',
            'Cutlassfish_202409_202508.xlsx'
            ]
func = pf.PublicFunc()
tempList = []
for item in fileName:
    cutlassFish = func.ReadExcel(
        filePath=filePath,
        fileName=item,
        sheetname=1,
        skiprows=5
        )
    tempList.append(cutlassFish)

df = func.MixData(tempList)
listCutlassFishLabel = ['날짜','생산','수입','전기재고','소비','수출','당기재고']
func.AddLabels(df,listCutlassFishLabel)


print(df.shape)
func.SaveCSV(df,'cutl.csv')

func = pf.PublicFunc()

# 갈치
def CreateCutlassFish(filePath):
    fishList = []

    fileName = func.ReadFold(filePath)

    for file in fileName:
        cutlassFish = func.ReadExcel(
            filePath=filePath,
            fileName=file,
            sheetname=1,
            skiprows=5
            )
        fishList.append(cutlassFish)

    df = func.MixData(fishList)
    listCutlassFishLabel = ['날짜','생산','수입','전기재고','소비','수출','당기재고']
    func.AddLabels(df,listCutlassFishLabel)


    print(df.shape)
    func.SaveCSV(df,'CutlassFishAll.csv')

if __name__ == '__main__':
    filePath = './data/fish/Cutlassfish'

    CreateCutlassFish(filePath)
