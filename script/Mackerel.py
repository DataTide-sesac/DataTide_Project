import PublicFunc as pf
import pandas as pd

func = pf.PublicFunc()

# 고등어
def CreateMackerel(filePath):
    fishList = []

    fileName = func.ReadFold(filePath)

    for file in fileName:
        mackerel = func.ReadExcel(
            filePath=filePath,
            fileName=file,
            sheetname=1,
            skiprows=5
            )
        fishList.append(mackerel)

    df = func.MixData(fishList)
    listMackerelLabel = ['날짜','생산','수입','전기재고','소비','수출','당기재고']
    func.AddLabels(df,listMackerelLabel)


    print(df.shape)
    func.SaveCSV(df,'MackerelAll.csv')

if __name__ == '__main__':
    filePath = './data/fish/Mackerel'
    
    CreateMackerel(filePath)