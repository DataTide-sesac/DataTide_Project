import PublicFunc as pf
import pandas as pd

filePath = './data/fish/Calamari'
fileName = ['calamari_201501_201508.xlsx',
            'calamari_201509_201608.xlsx',
            'calamari_201609_201708.xlsx',
            'calamari_201709_201808.xlsx',
            'calamari_201809_201908.xlsx',
            'calamari_201909_202008.xlsx',
            'calamari_202009_202108.xlsx',
            'calamari_202109_202208.xlsx',
            'calamari_202209_202308.xlsx',
            'calamari_202309_202408.xlsx',
            'calamari_202409_202508.xlsx'
            ]
func = pf.PublicFunc()
tempList = []
for item in fileName:
    calamari = func.ReadExcel(
        filePath=filePath,
        fileName=item,
        sheetname=1,
        skiprows=5
        )
    tempList.append(calamari)

df = func.MixData(tempList)
listCalamariLabel = ['날짜','생산','수입','전기재고','소비','수출','당기재고']
func.AddLabels(df,listCalamariLabel)


print(df.shape)
func.SaveCSV(df,'CalamariAll.csv')