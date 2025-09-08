import PublicFunc as pf
from datetime import datetime
func = pf.PublicFunc()

def FishDataCreate(filePath,fileName,fishName):
    df = func.ReadCSV(filePath,fileName)
    df = df.loc[:,['날짜','생산','수입','소비','수출']]
    df['수입'] = df['생산'].str.replace(',','')
    df['생산'] = df['수입'].str.replace(',','')
    df['소비'] = df['소비'].str.replace(',','')
    df['수출'] = df['수출'].str.replace(',','')

    df['수입'] = df['수입'].str.replace('-','0').astype(int)
    df['생산'] = df['생산'].str.replace('-','0').astype(int)
    df['소비'] = df['소비'].str.replace('-','0').astype(int)
    df['수출'] = df['수출'].str.replace('-','0').astype(int)


    df['판매'] = df[['소비','수출']].sum(axis=1).astype(int)

    df = df[df['날짜'].str.contains('2025')&
            ~df['날짜'].str.contains('08')]

    df.reset_index(drop=True, inplace=True)
    for i, item in enumerate(df['날짜']):
        dt = datetime.strptime(item, '%Y년 %m월')
        df.loc[i,'날짜'] = dt.strftime('%Y-%m-%d')


    df = df.loc[:,['날짜','생산','수입','판매']]

    df.insert(0,'품목명',fishName)

    func.SaveCSV(df,f'{fishName}_2025.csv')

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