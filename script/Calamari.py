import PublicFunc as pf
import pandas as pd

func = pf.PublicFunc()

# 오징어
def CreateCalamari(filePath):
    fishList = []

    fileName = func.ReadFold(filePath)

    for file in fileName:
        calamari = func.ReadExcel(
            filePath=filePath,
            fileName=file,
            sheetname=1,
            skiprows=5
            )
        fishList.append(calamari)

    df = func.MixData(fishList)
    listCalamariLabel = ['날짜','생산','수입','전기재고','소비','수출','당기재고']
    func.AddLabels(df,listCalamariLabel)

    print(df.shape)
    func.SaveCSV(df,'CalamariAll.csv')

if __name__ == '__main__':
    filePath = './data/fish/Calamari'
    
    CreateCalamari(filePath)