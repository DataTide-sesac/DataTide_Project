import PublicFunc as pf
import pandas as pd

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