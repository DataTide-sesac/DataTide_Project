import PublicFunc as pf
import pandas as pd

filePath = './data/fish/Mackerel'
fileName = ['mackerel_201501_201508.xlsx',
            'mackerel_201509_201608.xlsx',
            'mackerel_201609_201708.xlsx',
            'mackerel_201709_201808.xlsx',
            'mackerel_201809_201908.xlsx',
            'mackerel_201909_202008.xlsx',
            'mackerel_202009_202108.xlsx',
            'mackerel_202109_202208.xlsx',
            'mackerel_202209_202308.xlsx',
            'mackerel_202309_202408.xlsx',
            'mackerel_202409_202508.xlsx'
            ]
func = pf.PublicFunc()
tempList = []
for item in fileName:
    mackerel = func.ReadExcel(
        filePath=filePath,
        fileName=item,
        sheetname=1,
        skiprows=5
        )
    tempList.append(mackerel)

df = func.MixData(tempList)
listMackerelLabel = ['날짜','생산','수입','전기재고','소비','수출','당기재고']
func.AddColumns(df,listMackerelLabel)


print(df.shape)
func.SaveCSV(df,'MackerelAll.csv')