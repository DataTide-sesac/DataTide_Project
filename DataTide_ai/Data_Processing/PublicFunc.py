import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle as pk
import tabula as tbl
import os
class PublicFunc():

    # 상대경로/파일이름.확장자
    # csv파일 읽기, encoding이 utf-8이 아닐경우 지정해 줄것. 한국어는 cp949가 많다고 함.
    @staticmethod
    def ReadCSV(filePath, fileName, skiprows=0, encoding='utf-8-sig'):
        try:
            df = pd.read_csv(f"{filePath}/{fileName}",skiprows=skiprows , encoding=encoding)
            print(df.head())
            print(df.columns)
            print(df.shape)
            print(df.info())
        except FileNotFoundError as e:
            print(f"{e}, 파일 못찾음")
            return None
        except ValueError as e:
            print(f"{e}, ValueError")
            return None
        return df
    
    # 폴더 읽기
    @staticmethod
    def ReadFold(filePath):
        folder_path = filePath
        items = os.listdir(folder_path)

        files = [f for f in items if os.path.isfile(os.path.join(folder_path,f))]

        return files

    # Excel 파일 읽기, encoding이 utf-8이 아닐경우 지정해 줄것. 한국어는 cp949가 많다고 함.
    @staticmethod
    def ReadExcel(filePath, fileName,sheetname=0 ,skiprows=0):
        try:
            df = pd.read_excel(f"{filePath}/{fileName}", sheet_name=sheetname, skiprows=skiprows)
            print(df.head())
            print(df.columns)
            print(df.shape)
            print(df.info())
        except FileNotFoundError as e:
            print(f"{e}, 파일 못찾음")
            return None
        except ValueError as e:
            print(f"{e}, ValueError")
            return None
        except TypeError as e:
            print(f"{e}, TypeError")
            return pd.DataFrame
        return df

    
    # pdf 추출 / Type = month / year
    @staticmethod
    def ReadPDF(filePath, fileName, type='month'):
        typeDic = {'month':27,'year':13}
        try:
            tables = tbl.read_pdf(f'{filePath}/{fileName}',pages='all',stream=True,pandas_options={'header':None})

            total_df_raw = None
            for df in tables:
                if df[0].astype(str).str.contains('TOTAL').any():
                    total_df_raw = df
                break
            
            if total_df_raw is not None:
                start_index = total_df_raw[total_df_raw[0].astype(str).str.contains('TOTAL')].index[0]

                result_df = total_df_raw.iloc[start_index : start_index + 3].copy()

                result_df.set_index(result_df.columns[1], inplace=True)

                result_df = result_df.drop(columns=result_df.columns[0])

                if type == 'month':
                    months = [f'{i}' for i in range(1,typeDic['month'])]
                elif type == 'year':
                    months = [f'{i}월' for i in range(1,typeDic['year'])]
                else:
                    print('타입 틀림')
                    return 0
                result_df.columns = months

                print("완료")
                return result_df
            else:
                print("못찾음")
        except FileNotFoundError as e:
            print(f'{e}, 파일 못찾음')
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
        
        
    # 라벨 달기
    # data : csv,xlsx파일
    # colList : List 형태로 올 것
    @staticmethod
    def AddLabels(data,colList):
        try:
            data.columns = colList
        except TypeError as e:
            print(f"{e}, TypeError")
            return data
        except IndexError as e:
            print(f"{e}, Index Error")
            return data
        except ValueError as e:
            print(f"{e}, ValueError")
            return data
        return data

    # 결측치 제거
    # 0으로 바꾸는 것이 아닌 NaN값 삭제함.
    @staticmethod
    def IsNullDel(df, thresh=1, axis=0):
        try:
            df = df.dropna(thresh=thresh,axis=axis)
            df.shape
        except IndexError as e:
            print(f"{e}, Index Error")
            return df
        except TypeError as e:
            print(f"{e}, TypeError")
            return df
        
        return df

    # None값 대체
    # data 에는 None값을 대체할 열을 대입(ex: 3번째 열 대체 -> a[a['열이름']] )
    @staticmethod
    def ChangeNull(data,value):
        try:
            data[data.isna()] = value
        except TypeError as e:
            print(f"{e}, TypeError")
            return data
        except IndexError as e:
            print(f"{e}, Index Error")
            return data
        except ValueError as e:
            print(f"{e}, ValueError")
            return data
        return data

    # concat data / list
    # 반드시 리스트 형태로 넣어 줄 것
    @staticmethod
    def MixData(data,axis=0):
        try:
            if not data:
                return pd.DataFrame()
            df_list = []
            for item in data:
                if isinstance(item, dict):
                    df_list.append(pd.DataFrame([item]))
                elif isinstance(item, pd.DataFrame):
                    df_list.append(item)
                else:
                    df_list.append(pd.DataFrame(item))

            
            print("------ 구조확인 -----")
            for i, item in enumerate(df_list):
                print(f"Index {i}: Type: {type(item)}, {item.shape}")

            print("------ 구조확인 -----")
            return pd.concat(df_list, ignore_index=True, axis=axis)
            
        except TypeError as e:
            print(f"{e}, TypeError")
            return pd.DataFrame()
        except ValueError as e:
            print(f"{e}, ValueError")
            return pd.DataFrame()
    
    # boxplot, figsize : 튜플, vert : 방향
    @staticmethod
    def ShowBoxplot(data,figsize=(8,6),vert=True):
        try:
            plt.figure(figsize=figsize)
            plt.boxplot(data, vert=vert)
            plt.show()

        except TypeError as e:
            print(f"{e}, TypeError")
        except IndexError as e:
            print(f"{e}, Index Error")
        except ValueError as e:
            print(f"{e}, ValueError")

    # 이상치의 하한과 상한 반환
    @staticmethod
    def OutFiliersIqr(data):
        try:
            q1, q3 = np.percentile(data, [25,75])
            iqr = q3 - q1
            lower_bound = q1 - iqr*1.5
            upper_bound = q1 + iqr*1.5
        except TypeError as e:
            print(f"{e}, TypeError")
        except IndexError as e:
            print(f"{e}, Index Error")
        except ValueError as e:
            print(f"{e}, ValueError")

        return lower_bound, upper_bound

    # 이상치 대체
    @staticmethod
    def ChangeIqr(data,lb,ub):
        data = data.copy()
        try:
            data[data<lb] = lb
            data[data>ub] = ub
        except TypeError as e:
            print(f"{e}, TypeError")
            return data
        except IndexError as e:
            print(f"{e}, Index Error")
            return data
        except ValueError as e:
            print(f"{e}, ValueError")
            return data
        return data

    # 열 추가
    @staticmethod
    def AddColumns(df,index=0,column='',value=''):
        try:
            df.insert(index,column,value)
        except TypeError as e:
            print(f'{e}, TyperError')

    # 저장
    @staticmethod
    def SaveCSV(df,fileName='',encoding='utf-8-sig'):
        try:
            df.to_csv(fileName, index=False, encoding=encoding)
            print('save 완료')
        except FileNotFoundError as e:
            print(f"{e}, File 못찾음")
