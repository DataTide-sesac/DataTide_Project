import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from torch.utils.data import Dataset, DataLoader, random_split
import torch
import torch.nn as nn
import pymysql, os, calendar
from sqlalchemy import create_engine
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../..", ".env"))

# ======================
# 1. MySQL 연결
# ======================
# 본인 환경에 맞게 수정하세요
USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
HOST = "localhost"
PORT = 3306
DB = os.getenv("MYSQL_DATABASE")

db_con = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
# print(db_con)

# SQLAlchemy 엔진 생성
engine = create_engine(db_con)

# ======================
# 2. 테이블 불러오기
# ======================
item = pd.read_sql("SELECT * FROM item", engine)
monthly_avg = pd.read_sql("""SELECT MONTH(month_date) AS month,
                                AVG(temperature) AS temperature,
                                AVG(rain) AS rain
                            FROM ground_weather
                            WHERE YEAR(month_date) IN (2022, 2023, 2024, 2025)
                            GROUP BY MONTH(month_date)
                            ORDER BY month""", engine)


# ======================
# 3. 테이블 머지 (JOIN)
# ======================

# month를 month_date 형태로 변환 (예: 1 -> 2025-01-01, 2 -> 2025-02-01 등)
monthly_avg['month_date'] = pd.to_datetime(monthly_avg['month'].astype(str) + '-01', format='%m-%d')
monthly_avg['month_date'] = monthly_avg['month_date'].apply(lambda x: x.replace(year=2025))  # 년도를 2025로 설정
# 2025-01-01만 2026-01-01로 변경
monthly_avg.loc[monthly_avg['month_date'] == pd.Timestamp('2025-01-01'), 'month_date'] = pd.Timestamp('2026-01-01')
monthly_avg.loc[monthly_avg['month_date'] == pd.Timestamp('2025-02-01'), 'month_date'] = pd.Timestamp('2026-02-01')

# 2. 2025-08부터 6개월치 계산
start_date = pd.Timestamp('2025-07-01')
end_date = pd.Timestamp('2025-08-01') + pd.DateOffset(months=7)

monthly_avg_filtered = monthly_avg[(monthly_avg['month_date'] >= start_date) & 
                                   (monthly_avg['month_date'] <= end_date)].copy()

# 3. 기존 month 컬럼 제거
monthly_avg_filtered = monthly_avg_filtered.drop('month', axis=1)

print(monthly_avg_filtered)

print("최근 3년간 월별 평균 기온 및 강수량:")
print(monthly_avg_filtered)

# monthly_avg와 item을 교차 조인하여 모든 조합 생성
# 각 month_date마다 모든 품명이 포함되도록
monthly_avg_filtered['key'] = 1
item['key'] = 1
monthly_item_combo = monthly_avg_filtered.merge(item, on='key').drop('key', axis=1)

print("\monthly_avg_filtered item 조합:")
print(monthly_item_combo.head(10))
print(f"총 조합 개수: {len(monthly_item_combo)} (월 수: {len(monthly_avg_filtered)} x 품명 수: {len(item)})")

df = monthly_item_combo
# 날짜 정렬 
df["month_date"] = pd.to_datetime(df["month_date"]) 
df = df.sort_values(["month_date"]).reset_index(drop=True) 
df["month_num"] = df["month_date"].dt.year * 12 + df["month_date"].dt.month 
df = pd.get_dummies(df, columns=['item_name']) 

df.to_csv("predict_sales.csv", index=False, encoding="utf-8-sig")

def create_future_months_data(current_year, current_month, monthly_avg, df, months_ahead=6):
    """
    미래 6개월간의 예측 데이터를 생성하는 함수
    """
    future_data = []
    
    for i in range(1, months_ahead + 1):
        # 미래 월 계산
        future_month = current_month + i
        future_year = current_year
        
        # 년도 넘어가는 경우 처리
        if future_month > 12:
            future_year += (future_month - 1) // 12
            future_month = ((future_month - 1) % 12) + 1
        
        # 해당 월의 첫번째 날
        future_date = datetime(future_year, future_month, 1)
        
        # 해당 월의 평균 기온, 강수량 가져오기
        month_weather = monthly_avg[monthly_avg['month'] == future_month]
        
        if len(month_weather) > 0:
            avg_temp = month_weather['temperature'].iloc[0]
            avg_rain = month_weather['rain'].iloc[0]
        else:
            # 해당 월 데이터가 없으면 전체 평균 사용
            avg_temp = monthly_avg['temperature'].mean()
            avg_rain = monthly_avg['rain'].mean()
        
        # 미래 데이터 생성 (기존 데이터의 구조를 참고해서)
        future_row = {
            'month_date': future_date,
            'temperature': avg_temp,
            'rain': avg_rain,
            'month_num': future_year * 12 + future_month,
            'year': future_year,
            'month': future_month
        }
        
        # item_name 더미 변수들을 0으로 초기화 (또는 특정 아이템만 1로 설정)
        item_dummy_cols = [col for col in df.columns if col.startswith('item_name_')]
        for col in item_dummy_cols:
            future_row[col] = 0
        
        # 만약 특정 아이템만 예측하고 싶다면 해당 아이템만 1로 설정
        # 예: future_row['item_name_특정아이템'] = 1
        
        future_data.append(future_row)
    
    return pd.DataFrame(future_data)

# 미래 6개월 데이터 생성
# future_df = create_future_months_data(2025, 7, monthly_avg, df, months_ahead=6)
# print("\n미래 6개월 예측 데이터:")
# print(future_df)

class TimeSeriesDataset(Dataset):
    def __init__(self, df, feature_cols, target_cols, window_size=6):
        self.window_size = window_size
        self.features = df[feature_cols].values
        self.targets = df[target_cols].values

        # 표준화
        self.scaler_x = StandardScaler()
        self.scaler_y = StandardScaler()

        self.features = self.scaler_x.fit_transform(self.features)
        self.targets = self.scaler_y.fit_transform(self.targets)

    def __len__(self):
        return len(self.features) - self.window_size

    def __getitem__(self, idx):
        X = self.features[idx:idx+self.window_size]
        y = self.targets[idx+self.window_size]
        return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

class GRUModel_2hidden(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=2, num_layers=2):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True)
        self.relu = nn.ReLU()

        self.fc = nn.Linear(hidden_dim, output_dim)
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.fc2 = nn.Linear(64, output_dim)

    def forward(self, x):
        _, h_n = self.gru(x)
        out = h_n[-1]
        # out = self.fc(out)

        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)  # 마지막 hidden state
        return out

# target_cols = ["sales"]
feature_cols = [x for x in df.columns if x not in ["month_date", "production", "sales", "ground_pk", "item_pk", "retail_pk", "inbound"]]

model = GRUModel_2hidden(input_dim=len(feature_cols), hidden_dim=64, output_dim=1)
model.load_state_dict(torch.load("./GRU_models/GRU_2hidden_sales.pth"))
model.eval()  # 평가 모드

# 미래 데이터에서 feature_cols에 해당하는 컬럼들만 추출
future_features = df[feature_cols]

# 스케일링이 필요한 경우 (기존 학습 데이터로 fit된 scaler 필요)
features = df[feature_cols].values

# 표준화
scaler_x = StandardScaler()
features = scaler_x.fit_transform(features)

print(f"\n예측용 특성 데이터 형태: {future_features.shape}")
print("특성 컬럼들:", feature_cols[:5], "..." if len(feature_cols) > 5 else "")

# 텐서로 변환 (시퀀스 데이터로 만들기 - GRU는 3차원 입력 필요: [batch_size, sequence_length, features])
future_tensor = torch.FloatTensor(features).unsqueeze(0)  # batch_size=1, sequence_length=6, features=len(feature_cols)

print(f"입력 텐서 형태: {future_tensor.shape}")

window_size = 6
predictions_list = []
# 예측 수행
with torch.no_grad(): 
    for i in range(len(features) - window_size):
        x_seq = features[i:i+window_size]
        x_seq = torch.FloatTensor(x_seq).unsqueeze(0)  # [1, window_size, feature_dim]
        pred = model(x_seq)
        predictions_list.append(pred.cpu().numpy()[0,0])

print("예측 결과:")

# 결과를 DataFrame으로 정리
# DataFrame에 맞추기 (앞 window_size 행은 NaN)
results_df = df[['month_date', 'temperature', 'rain']].copy()
results_df['predicted_sales'] = [np.nan]*window_size + predictions_list

print("\n=== 미래 6개월 예측 결과 ===")
for idx, row in results_df.iterrows():
    print(f"{row['month_date'].strftime('%Y년 %m월')}: "
          f"기온 {row['temperature']:.1f}°C, "
          f"강수량 {row['rain']:.1f}mm, "
          f"예상 판매량 {row['predicted_sales']:.2f}")

# CSV로 저장
results_df.to_csv('future_6months_prediction.csv', index=False, encoding='utf-8-sig')
print(f"\n예측 결과가 'future_6months_prediction.csv'로 저장되었습니다.")