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
                                ROUND(AVG(temperature), 1) AS temperature,
                                ROUND(AVG(rain), 1) AS rain
                            FROM ground_weather
                            WHERE YEAR(month_date) IN (2022, 2023, 2024, 2025)
                            GROUP BY MONTH(month_date)
                            ORDER BY month""", engine)
past_month = pd.read_sql("""SELECT * FROM ground_weather
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

print(monthly_avg_filtered)

print("최근 3년간 월별 평균 기온 및 강수량:")
print(monthly_avg_filtered)

# monthly_avg와 item을 교차 조인하여 모든 조합 생성
# 각 month_date마다 모든 품명이 포함되도록
monthly_avg_filtered['key'] = 1
past_month['key'] = 1
item['key'] = 1
monthly_item_combo = monthly_avg_filtered.merge(item, on='key').drop('key', axis=1)
past_month = past_month.merge(item, on='key').drop('key', axis=1)

print("\monthly_avg_filtered item 조합:")
print(monthly_item_combo.head(10))
print(f"총 조합 개수: {len(monthly_item_combo)} (월 수: {len(monthly_avg_filtered)} x 품명 수: {len(item)})")

df = pd.concat([past_month, monthly_item_combo], ignore_index=True)
# 날짜 정렬 
df["month_date"] = pd.to_datetime(df["month_date"]) 
df = df.sort_values(["month_date"]).reset_index(drop=True) 
df["month_num"] = df["month_date"].dt.year * 12 + df["month_date"].dt.month 
df = pd.get_dummies(df, columns=['item_name']) 

df.to_csv("predict_sales.csv", index=False, encoding="utf-8-sig")

class GRUModel_1hidden(nn.Module):
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
        out = self.fc(out)

        # out = self.fc1(h_n[-1])
        # out = self.relu(out)
        # out = self.fc2(out)  # 마지막 hidden state
        return out
    
class GRUModel_1hidden_32(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=2, num_layers=2):
        super().__init__()
        self.gru = nn.GRU(input_dim, 32, num_layers, batch_first=True)
        self.relu = nn.ReLU()

        self.fc = nn.Linear(32, output_dim)
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.fc2 = nn.Linear(64, output_dim)

    def forward(self, x):
        _, h_n = self.gru(x)
        out = h_n[-1]
        out = self.fc(out)

        # out = self.fc1(out)
        # out = self.relu(out)
        # out = self.fc2(out)  # 마지막 hidden state
        return out

# target_cols = ["sales"]
feature_cols = [x for x in df.columns if x not in ["month_date", "production", "sales", "ground_pk", "item_pk", "retail_pk", "inbound"]]

def model_32():
    model = GRUModel_1hidden_32(input_dim=len(feature_cols), hidden_dim=64, output_dim=1)
    model.load_state_dict(torch.load("./GRU_models/GRU_1hidden_32_sales.pth"))
    model.eval()  # 평가 모드
    return model

def model_1hidden():
    model = GRUModel_1hidden(input_dim=len(feature_cols), hidden_dim=64, output_dim=1)
    model.load_state_dict(torch.load("./GRU_models/GRU_1hidden_sales.pth"))
    model.eval()  # 평가 모드
    return model

model = model_1hidden()

# 미래 데이터에서 feature_cols에 해당하는 컬럼들만 추출
future_features = df[feature_cols]

# 스케일링이 필요한 경우 (기존 학습 데이터로 fit된 scaler 필요)
features = df[feature_cols].values

# 표준화
scaler_x = joblib.load("sales_scaler_x.pkl")
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
# 더미 컬럼 이름들
dummy_cols = [col for col in df.columns if col.startswith('item_name_')]

# 각 행에서 값이 1인 컬럼을 찾아 item_name으로 복원
df['item_name'] = df[dummy_cols].idxmax(axis=1).str.replace('item_name_', '', regex=False)

# 원래 더미 컬럼 삭제
df = df.drop(columns=dummy_cols)

# DataFrame에 맞추기 (앞 window_size 행은 NaN)
# results_df = df[['month_date', 'temperature', 'rain']].copy()
results_df = df.copy()
results_df['predicted_sales'] = [np.nan]*window_size + predictions_list

scaler_y = joblib.load("sales_scaler_y.pkl")
y_pred_original = scaler_y.inverse_transform(results_df['predicted_sales'].values.reshape(-1, 1))
results_df['sales'] = y_pred_original.flatten()
results_df['month_date'] = results_df['month_date'].dt.date

# 매핑 딕셔너리
item_map = {
    "Calamari": 1,
    "CutlassFish": 2,
    "Mackerel": 3
}

# item_name 컬럼 숫자로 변환
results_df['item_pk'] = results_df['item_name'].map(item_map)


print("\n=== 미래 6개월 예측 결과 ===")
for idx, row in results_df.iterrows():
    print(f"{row['month_date'].strftime('%Y년 %m월')}: "
          f"기온 {row['temperature']:.1f}°C, "
          f"강수량 {row['rain']:.1f}mm, "
          f"예상 판매량(복구) {row['sales']:.2f}")

# CSV로 저장
results_df.to_csv('future_6months_prediction.csv', index=False, encoding='utf-8-sig')
print(f"\n예측 결과가 'future_6months_prediction.csv'로 저장되었습니다.")

def predictAdd(results_df: pd.DataFrame):
    with engine.begin() as conn:  # 트랜잭션 자동 처리
        #외래키 제약 제거
        conn.execute(text('SET FOREIGN_KEY_CHECKS = 0;'))

        #테이블 삭제
        conn.execute(text(f'''
                            DROP TABLE 
                            item_predict
                            '''))
        
        # item_predict
        conn.execute(text(f'''
                    create table item_predict(
                    predict_pk BIGINT PRIMARY key AUTO_INCREMENT,
                    item_pk int,
                    month_date date,
                    production int,
                    inbound int,
                    sales int,
                    
                    FOREIGN KEY (item_pk) REFERENCES item(item_pk)
                );
                '''))

    # --- 기존 테이블 불러오기 ---
    existing_df = pd.read_sql("SELECT * FROM item_predict", con=engine)

    cols_to_keep = ['item_pk', 'month_date', 'sales']
    results_df = results_df[cols_to_keep]

    # --- 기존 데이터와 합치기 ---
    combined_df = pd.concat([existing_df, results_df])
    # --- 중복 제거 (month_date + item_pk 기준) ---
    combined_df = combined_df.drop_duplicates(subset=['month_date', 'item_pk'], keep='last')
    
    # --- DB에 저장 (덮어쓰기) ---
    combined_df.to_sql('item_predict', con=engine, if_exists='replace', index=False)

    print("예측 데이터가 기존 테이블에 추가/업데이트 되었습니다.")


predictAdd(results_df)