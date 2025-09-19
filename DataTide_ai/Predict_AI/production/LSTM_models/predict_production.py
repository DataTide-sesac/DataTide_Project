import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from torch.utils.data import Dataset, DataLoader, random_split
import torch
import torch.nn as nn
import pymysql, os, calendar
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime
import joblib

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../..", ".env"))

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
location = pd.read_sql("SELECT * FROM location", engine)
item_retail = pd.read_sql("SELECT * FROM item_retail", engine)
monthly_avg = pd.read_sql("""SELECT MONTH(month_date) AS month,
                                ROUND(AVG(temperature), 1) AS temperature,
                                ROUND(AVG(wind), 1) AS wind,
                                ROUND(AVG(salinity), 1) AS salinity,
                                ROUND(AVG(wave_height), 1) AS wave_height,
                                ROUND(AVG(wave_period), 1) AS wave_period,
                                ROUND(AVG(wave_speed), 1) AS wave_speed,
                                ROUND(AVG(rain), 1) AS rain,
                                ROUND(AVG(snow), 1) AS snow
                            FROM sea_weather
                            WHERE YEAR(month_date) IN (2022, 2023, 2024, 2025)
                            GROUP BY MONTH(month_date)
                            ORDER BY month""", engine)

past_month = pd.read_sql("""SELECT local_pk, month_date, temperature,
                          wind, salinity, wave_height, wave_period, wave_speed, rain, snow
                          FROM sea_weather
                          WHERE YEAR(month_date) IN (2025)"""
                          , engine)
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
start_date = pd.Timestamp('2025-08-01')
end_date = pd.Timestamp('2025-08-01') + pd.DateOffset(months=7)

monthly_avg_filtered = monthly_avg[(monthly_avg['month_date'] >= start_date) & 
                                   (monthly_avg['month_date'] <= end_date)].copy()

# 3. 기존 month 컬럼 제거
monthly_avg_filtered = monthly_avg_filtered.drop('month', axis=1)

monthly_avg_filtered['key'] = 1
location['key'] = 1
monthly_avg_filtered = monthly_avg_filtered.merge(location, on='key').drop('key', axis=1)
print(monthly_avg_filtered.head())
location = location.drop('key', axis=1)
past_month = past_month.merge(location, on="local_pk", how="left")

monthly_avg_filtered['key'] = 1
item['key'] = 1
monthly_avg_filtered = monthly_avg_filtered.merge(item, on='key').drop('key', axis=1)
print(monthly_avg_filtered.head())
item = item.drop('key', axis=1)

df = item_retail.merge(past_month, on="month_date", how="right")
df = df.merge(item, on="item_pk", how="left")

print("past_month 컬럼 : ", past_month.columns)
print("monthly_avg_filtered 컬럼 : ", monthly_avg_filtered.columns)
df = pd.concat([past_month, monthly_avg_filtered], ignore_index=True)
print(df.head())

# 날짜 정렬 
df["month_date"] = pd.to_datetime(df["month_date"]) 
df = df.sort_values(["month_date"]).reset_index(drop=True) 
df["month_num"] = df["month_date"].dt.year * 12 + df["month_date"].dt.month 
df = pd.get_dummies(df, columns=['item_name']) 
df = pd.get_dummies(df, columns=['local_name'])

df.to_csv("predict_production.csv", index=False, encoding="utf-8-sig")

class LSTMModel_1hidden(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=1, num_layers=2):
        super(LSTMModel_1hidden, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.relu = nn.ReLU()

        self.fc = nn.Linear(hidden_dim, output_dim)
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.fc2 = nn.Linear(64, output_dim)

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        out = h_n[-1]
        out = self.fc(out)

        # out = self.fc1(h_n[-1])
        # out = self.relu(out)
        # out = self.fc2(out)  # 마지막 hidden state
        return out
    
class LSTMModel_1hidden_32(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=1, num_layers=2):
        super(LSTMModel_1hidden_32, self).__init__()
        self.lstm = nn.LSTM(input_dim, 32, num_layers, batch_first=True)
        self.relu = nn.ReLU()

        self.fc = nn.Linear(32, output_dim)
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.fc2 = nn.Linear(64, output_dim)

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        out = h_n[-1]
        out = self.fc(out)

        # out = self.fc1(h_n[-1])
        # out = self.relu(out)
        # out = self.fc2(out)  # 마지막 hidden state
        return out

target_cols = ["production"]
feature_cols = [x for x in df.columns if x not in ["month_date", "production", "sales", "inbound", "item_pk", "retail_pk", "item_pk", "local_pk", "sea_pk",
                                                   "item_name", "local_name"]]

def model_1hidden():
    model = LSTMModel_1hidden(input_dim=len(feature_cols), hidden_dim=64, output_dim=1)
    model.load_state_dict(torch.load("./LSTM_1hidden_production.pth"))
    model.eval()  # 평가 모드
    return model

def model_1_32():
    model = LSTMModel_1hidden_32(input_dim=len(feature_cols), hidden_dim=64, output_dim=1)
    model.load_state_dict(torch.load("./RMSprop/LSTM_1hidden_32_production.pth"))
    model.eval()  # 평가 모드
    return model

model = model_1_32()

# 미래 데이터에서 feature_cols에 해당하는 컬럼들만 추출
future_features = df[feature_cols]

# 스케일링이 필요한 경우 (기존 학습 데이터로 fit된 scaler 필요)
features = df[feature_cols].values

# 표준화
scaler_x = joblib.load("production_scaler_x.pkl")
features = scaler_x.transform(features)

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
# 더미 컬럼 이름들
item_dummy_cols = [col for col in df.columns if col.startswith('item_name_')]
local_dummy_cols = [col for col in df.columns if col.startswith('local_name_')]

# 각 행에서 값이 1인 컬럼을 찾아 item_name으로 복원
df['item_name'] = df[item_dummy_cols].idxmax(axis=1).str.replace('item_name_', '', regex=False)
df['local_name'] = df[local_dummy_cols].idxmax(axis=1).str.replace('local_name_', '', regex=False)


# 원래 더미 컬럼 삭제
df = df.drop(columns=item_dummy_cols)
df = df.drop(columns=local_dummy_cols)

# DataFrame에 맞추기 (앞 window_size 행은 NaN)
# results_df = df[['month_date', 'temperature', 'rain']].copy()
results_df = df.copy()
results_df['predicted_production'] = [np.nan]*window_size + predictions_list

scaler_y = joblib.load("production_scaler_y.pkl")
y_pred_original = scaler_y.inverse_transform(results_df['predicted_production'].values.reshape(-1, 1))
results_df['production'] = y_pred_original.flatten()
results_df['month_date'] = results_df['month_date'].dt.date

# 매핑 딕셔너리
item_map = {
    "Calamari": 1,
    "CutlassFish": 2,
    "Mackerel": 3
}

# 매핑 딕셔너리
local_map = {
    "강원": 1,
    "경기": 2,
    "경북": 3,
    "부산": 4,
    "전남": 5,
    "전북": 6,
    "제주": 7,
    "충남": 8,
    "통영": 9
}
	

# item_name 컬럼 숫자로 변환
results_df['item_pk'] = results_df['item_name'].map(item_map)
results_df['local_pk'] = results_df['local_name'].map(local_map)
results_df = results_df.drop('predicted_production', axis=1)

df_grouped = results_df.groupby(["month_date", "item_pk"], as_index=False)["production"].mean()


print("\n=== 미래 6개월 예측 결과 ===")
for idx, row in df_grouped.iterrows():
    print(f"{row['month_date'].strftime('%Y년 %m월')}: "
          f"품목 {row['item_pk']}, "
          f"예상 생산량(복구) {row['production']:.2f}")

# CSV로 저장
print(df_grouped.head())
df_grouped.to_csv('grouped_future.csv', index=False, encoding='utf-8-sig')
# results_df.to_csv('future_6months_prediction.csv', index=False, encoding='utf-8-sig')
print(f"\n예측 결과가 'grouped_future.csv'로 저장되었습니다.")

def predictAdd(df_grouped: pd.DataFrame):
    cols_to_keep = ['item_pk', 'month_date', 'production']
    df_grouped = df_grouped[cols_to_keep]

    # DB에 upsert (중복 시 update)
    with engine.begin() as conn:
        for _, row in df_grouped.iterrows():
            conn.execute(text("""
                INSERT INTO item_predict (item_pk, month_date, production)
                VALUES (:item_pk, :month_date, :production)
                ON DUPLICATE KEY UPDATE
                    production = VALUES(production)
            """), row.to_dict())

    print("예측 데이터가 item_predict 테이블에 upsert 되었습니다.")


predictAdd(df_grouped)

def predictInbound():
    import math

    # --- 기존 테이블 불러오기 ---
    existing_df = pd.read_sql("SELECT item_pk, month_date, production, sales FROM item_predict", con=engine)

    # DB에 upsert (중복 시 update)
    with engine.begin() as conn:
        for _, row in existing_df.iterrows():
            values = row.to_dict()
            # NaN 안전 처리
            sales = values.get('sales', 0)
            production = values.get('production', 0)

            # NaN이면 0으로 대체
            if sales is None or (isinstance(sales, float) and math.isnan(sales)):
                sales = 0
            if production is None or (isinstance(production, float) and math.isnan(production)):
                production = 0

            values['inbound'] = sales - production
            if values['inbound'] < 0:
                values['inbound'] = 0

            cols_to_keep = ['item_pk', 'month_date', 'inbound']
            values = {k: values[k] for k in cols_to_keep}
            print(values)
            conn.execute(text("""
                INSERT INTO item_predict (item_pk, month_date, inbound)
                VALUES (:item_pk, :month_date, :inbound)
                ON DUPLICATE KEY UPDATE
                    inbound = VALUES(inbound)
            """), values)

    print("예측 데이터가 item_predict 테이블에 upsert 되었습니다.")

predictInbound()