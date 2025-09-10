import PublicFunc as pf
from datetime import datetime
func = pf.PublicFunc()

# 물고기 데이터 전처리
def FishDataCreate(filePath,fileName,fishName):
    df = func.ReadCSV(filePath,fileName)
    typeList = ['생산','수입','소비','수출']
    df = df.loc[:,['날짜','생산','수입','소비','수출']]

    for type in typeList:
        df[type] = df[type].str.replace(',','')
        df[type] = df[type].str.replace('-','0').astype(int)


    df['판매'] = df[['소비','수출']].sum(axis=1).astype(int)

    df = df[~df['날짜'].str.contains('2025-08')]

    df.reset_index(drop=True, inplace=True)
    for i, item in enumerate(df['날짜']):
        dt = datetime.strptime(item, '%Y년 %m월')
        df.loc[i,'날짜'] = dt.strftime('%Y-%m-%d')


    df = df.loc[:,['날짜','생산','수입','판매']]

    df.insert(0,'품목명',fishName)

    func.SaveCSV(df,f'{fishName}.csv')

if __name__ == '__main__':
    filePath = './data/fish/AllData'
    fileName = 'CutlassfishAll.csv'
    fishName = 'CutlassFish'
    FishDataCreate(filePath,fileName,fishName)
    
    fileName = 'CalamariAll.csv'
    fishName = 'Calamari'
    FishDataCreate(filePath,fileName,fishName)
    
    fileName = 'MackerelAll.csv'
    fishName = 'Mackerel'
    FishDataCreate(filePath,fileName,fishName)