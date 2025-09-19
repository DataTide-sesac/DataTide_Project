import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from torch.utils.data import Dataset, DataLoader, random_split
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm
import pymysql, os
from sqlalchemy import create_engine
from dotenv import load_dotenv

import seaborn as sns
import matplotlib.pyplot as plt
import wandb
from sklearn.preprocessing import LabelEncoder
import joblib

# --- 환경변수 불러오기 ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../DataTide_front", ".env"))

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
item_retail = pd.read_sql("SELECT * FROM item_retail", engine)
sea_weather = pd.read_sql("SELECT * FROM sea_weather", engine)
ground_weather = pd.read_sql("SELECT * FROM ground_weather", engine)
location = pd.read_sql("SELECT * FROM location", engine)
item = pd.read_sql("SELECT * FROM item", engine)

print("item_retail sample:")
print(item_retail.head())

# ======================
# 3. 테이블 머지 (JOIN)
# ======================
def read_df_1():
    item_retail = pd.read_sql("SELECT * FROM item_retail", engine)
    sea_weather = pd.read_sql("SELECT * FROM sea_weather", engine)
    ground_weather = pd.read_sql("SELECT * FROM ground_weather", engine)
    location = pd.read_sql("SELECT * FROM location", engine)
    item = pd.read_sql("SELECT * FROM item", engine)

    # sea_weather wide-format 변환
    sea_weather = sea_weather.merge(location, on="local_pk", how="left")
    sea_weather_wide = sea_weather.pivot(
        index="month_date", 
        columns="local_pk", 
        values=["temperature", "wind", "salinity", "wave_height", "wave_period", "wave_speed", "rain", "snow"]
    )

    # 컬럼명 정리
    sea_weather_wide.columns = [f"{var}_loc{loc}" for var, loc in sea_weather_wide.columns]
    sea_weather_wide = sea_weather_wide.reset_index()
    print(sea_weather_wide)

    df = item_retail.merge(sea_weather_wide, on="month_date", how="left")
    # df = df.merge(ground_weather, on="month_date", how="left")
    df = df.merge(item, on="item_pk", how="left")

    # 날짜 정렬
    df["month_date"] = pd.to_datetime(df["month_date"])
    df = df.sort_values(["month_date"]).reset_index(drop=True)
    df["month_num"] = df["month_date"].dt.year * 12 + df["month_date"].dt.month
    df = pd.get_dummies(df, columns=['item_name'])

    print("Merged DataFrame:")
    print(df.head())
    df.to_csv("compare_production1.csv", index=False, encoding="utf-8-sig")

    return df

def read_df_2():
    item_retail = pd.read_sql("SELECT * FROM item_retail", engine)
    sea_weather = pd.read_sql("SELECT * FROM sea_weather", engine)
    ground_weather = pd.read_sql("SELECT * FROM ground_weather", engine)
    location = pd.read_sql("SELECT * FROM location", engine)
    item = pd.read_sql("SELECT * FROM item", engine)
    
    # sea_weather wide-format 변환
    sea_weather = sea_weather.merge(location, on="local_pk", how="left")

    df = item_retail.merge(sea_weather, on="month_date", how="left")
    # df = df.merge(ground_weather, on="month_date", how="left")
    df = df.merge(item, on="item_pk", how="left")

    # 날짜 정렬
    df["month_date"] = pd.to_datetime(df["month_date"])
    df = df.sort_values(["month_date"]).reset_index(drop=True)
    df["month_num"] = df["month_date"].dt.year * 12 + df["month_date"].dt.month
    df = pd.get_dummies(df, columns=['item_name'])
    df = pd.get_dummies(df, columns=['local_name'])

    print("Merged DataFrame:")
    print(df.head())
    df.to_csv("compare_production2.csv", index=False, encoding="utf-8-sig")

    return df

def read_df_3():
    item_retail = pd.read_sql("SELECT * FROM item_retail", engine)
    sea_weather = pd.read_sql("SELECT * FROM sea_weather", engine)
    location = pd.read_sql("SELECT * FROM location", engine)
    item = pd.read_sql("SELECT * FROM item", engine)
    
    # sea_weather wide-format 변환
    sea_weather = sea_weather.merge(location, on="local_pk", how="left")

    df = item_retail.merge(sea_weather, on="month_date", how="left")
    df = df.merge(item, on="item_pk", how="left")

    # 날짜 정렬
    df["month_date"] = pd.to_datetime(df["month_date"])
    df = df.sort_values(["month_date"]).reset_index(drop=True)
    df["month_num"] = df["month_date"].dt.year * 12 + df["month_date"].dt.month

    # 학습 단계
    item_le = LabelEncoder()
    local_le = LabelEncoder()

    df["item_id"] = item_le.fit_transform(df["item_name"])
    df["local_id"] = local_le.fit_transform(df["local_name"])

    print("Merged DataFrame:")
    print(df.head())
    df.to_csv("compare_production3.csv", index=False, encoding="utf-8-sig")

    # 인코더 저장
    joblib.dump(item_le, "item_encoder.pkl")
    joblib.dump(local_le, "local_encoder.pkl")

    return df

df = read_df_2()

# ======================
# 4. 시계열 윈도우 데이터셋 생성
# ======================
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

# ======================
# 5. PyTorch 모델 정의
# ======================
class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=1, num_layers=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        out = self.fc(h_n[-1])  # 마지막 hidden state
        return out

class SimpleRNNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=1, num_layers=2):
        super().__init__()
        self.rnn = nn.RNN(input_dim, hidden_dim, num_layers, batch_first=True)
        
        # 중간 hidden layer 추가
        self.hidden_layer = nn.Linear(hidden_dim, hidden_dim // 2)
        self.relu = nn.ReLU()

        self.fc = nn.Linear(hidden_dim // 2, output_dim)

    def forward(self, x):
        _, h_n = self.rnn(x)
       
        # 추가 hidden layer 통과
        h_n = self.hidden_layer(h_n[-1])     # (batch, hidden_dim//2)
        h_n = self.relu(h_n)

        out = self.fc(h_n)
        return out

class GRUModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, output_dim=1, num_layers=2):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        _, h_n = self.gru(x)
        out = self.fc(h_n[-1])
        return out

# feature embedding → Transformer Encoder → FC regression head
class TransformerEncoderModel(nn.Module):
    def __init__(self, input_dim, d_model=64, nhead=4, num_layers=2, output_dim=1):
        super().__init__()
        self.input_fc = nn.Linear(input_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, output_dim)

    def forward(self, x):
        x = self.input_fc(x)
        x = self.transformer(x)
        # 마지막 시점 선택
        out = self.fc(x[:, -1, :])
        return out
    
# ======================
# 6. 학습 루프
# ======================
def train_and_evaluate(model, train_loader, val_loader, epochs=40, lr=1e-3, model_name="model.pth"):
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    best_rmse = float("inf")  # 아주 큰 값으로 초기화
    best_mae = float("inf")  # 아주 큰 값으로 초기화
    best_r2 = float("inf")  # 아주 큰 값으로 초기화
    best_state = None

    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for X, y in train_loader:
            optimizer.zero_grad()
            preds = model(X)
            loss = criterion(preds, y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # 검증
        model.eval()
        val_loss = 0
        y_true, y_pred = [], []
        with torch.no_grad():
            for X, y in val_loader:
                preds = model(X)
                val_loss += criterion(preds, y).item()
                y_true.extend(y.numpy())
                y_pred.extend(preds.numpy())

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)

        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss/len(train_loader):.4f} | "
              f"Val Loss: {val_loss/len(val_loader):.4f} | RMSE: {rmse:.2f} | MAE: {mae:.2f} | R²: {r2:.2f}")
        
        # 🚀 wandb에 로그 기록
        wandb.log({
            "epoch": epoch+1,
            "train_loss": avg_train_loss,
            "val_loss": avg_val_loss,
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "model": model_name
        })

        # ✅ 가장 좋은 모델 저장
        if rmse < best_rmse:
            best_rmse = rmse
            best_mae = mae
            best_r2 = r2
            best_state = model.state_dict()
            torch.save(best_state, f"{model_name}_sales.pth")
            print(f"  👉 Best model saved (epoch {epoch+1}, RMSE={rmse:.2f})")


    # 최종 성능 리턴
    return best_rmse, best_mae, best_r2

# ======================
# 7. 실행
# ======================

# # 사용할 컬럼 정의 (예시)
target_cols = ["production"]
feature_cols = [x for x in df.columns if x not in ["month_date", "production", "sales", "item_pk", "retail_pk", "item_pk", "local_pk", "sea_pk",
                                                   "item_name", "local_name"]]

def do_pca():
    from sklearn.decomposition import PCA
    X = df[feature_cols].values  # sklearn은 numpy 입력

    # 표준화 (TimeSeriesDataset에서도 StandardScaler 했지만 PCA용 별도)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("X_scaled의 shape:", X_scaled.shape)

    # PCA 적용
    pca = PCA(n_components=21)  # 원하는 주성분 개수
    X_pca = pca.fit_transform(X_scaled)

    # shape 확인
    print(X_pca.shape)  # (num_samples, 20)

# # Dataset 준비
# dataset = TimeSeriesDataset(df, feature_cols, target_cols, window_size=6)
dataset = TimeSeriesDataset(df, feature_cols, target_cols, window_size=6)

# Train / Validation Split
train_size = int(len(dataset) * 0.8)
val_size = len(dataset) - train_size
train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# 모델 초기화
input_dim = len(feature_cols)

# 학습
models = {
    "LSTM": LSTMModel(input_dim=len(feature_cols), hidden_dim=64, output_dim=len(target_cols)),
    "SimpleRNN": SimpleRNNModel(input_dim=len(feature_cols), hidden_dim=64, output_dim=len(target_cols)),
    "GRU": GRUModel(input_dim=len(feature_cols), hidden_dim=64, output_dim=len(target_cols)),
    "Transformer": TransformerEncoderModel(input_dim=len(feature_cols), d_model=64, nhead=4, num_layers=2, output_dim=len(target_cols))
}

results = {}

for name, model in models.items():
    print(f"\n===== Training {name} =====")
    # 프로젝트명, 엔티티(계정명 또는 팀명), 하이퍼파라미터 기록
    wandb.init(
        project="DataTide_production_compare_model_3",   # 원하는 프로젝트 이름
        entity=os.getenv("WANDB_ENTITY"),       # 본인 계정명
        config={
            "epochs": 100,
            "learning_rate": 1e-3,
            "batch_size": 32,
            "window_size": 6,
            "hidden_dim": 64,
            "model":name
        },
        name=name,
        group="read-df-3_5",
        reinit=True   # run 새로 시작
    )
    rmse, mae, r2 = train_and_evaluate(model, train_loader, val_loader, 
                                       epochs=wandb.config.epochs, 
                                       lr=wandb.config.learning_rate, 
                                       model_name=name)
    results[name] = {"RMSE": rmse, "MAE": mae, "R2": r2}

print("\n===== Model Comparison =====")
for name, metric in results.items():
    print(f"{name}: RMSE={metric['RMSE']:.2f}, MAE={metric['MAE']:.2f}, R²={metric['R2']:.2f}")

def drawHitmap():
    # 히트맵.
    correlation_matrix = df[feature_cols + target_cols].corr()     # 데이터 프레임이 corr 이라는 함수가 있어서 상관계수를 계산한다.
    print(correlation_matrix[:10])

    # 2. 히트맵 그리기
    annot = False    # 차트에 줄 속성. 히트맵의 셀에 값을 표시한다. False면 표시 안 함.
    cmap = 'coolwarm'   # 히트맵에서 가장 많이 사용하는 색상. 양의관계는 빨간색, 음의관계는 파란색
    fmt = '.2f'     # 표시될 숫자의 소수점 자리수 지정
    sns.heatmap(correlation_matrix,
                annot=annot, cmap=cmap, fmt=fmt, 
                linewidths=.5)      # 셀 사이에 선 추가
    plt.xticks(rotation=45, ha='right')     #  x축 레이블 회전
    plt.yticks(rotation=0)
    plt.tight_layout()      # 레이블 겹침 방지. 다시 그려라
    plt.show()