import PublicFunc as pf
import os
func = pf.PublicFunc()

# 파일 이름 변경
def FileRename(filePath):
    localList = ['강원','경기','경북','부산','전남','전북','제주','충남','통영']
    yearList = ['2015','2016','2017','2018','2019','2020','2021','2022','2023','2024','2025']
    typeList = ['수온','염분','유속','유의파고','유의파주기','풍속']
    monthList = ['01','02','03','04','05','06','07','08','09','10','11','12']
    for local in localList:
        for year in yearList:
            for type in typeList:
                fileName = func.ReadFold(f'{filePath}/{local}/{year}_월간보고서/{type}')
                for file in fileName:
                    if '월간' in file:
                        for month in monthList:
                            if f'{year}_{month}' in file:
                                # 이전 파일 이름
                                oldFileName = os.path.join(f'{filePath}/{local}/{year}_월간보고서/{type}',file)
                                # 새로운 파일 이름
                                newFileName = os.path.join(f'{filePath}/{local}/{year}_월간보고서/{type}',f"{local}_{year}_{month}_{type}_월간보고서.pdf")
                                # 이미 파일 존재 시 삭제
                                if os.path.exists(newFileName):
                                    os.remove(newFileName)

                                # 파일 이름 변경
                                os.rename(oldFileName,newFileName)
                                break



if __name__ == '__main__':
    filePath = './data/sea_weather_data'
    FileRename(filePath)
