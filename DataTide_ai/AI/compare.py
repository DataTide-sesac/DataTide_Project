import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np

# ===============================
# 1. Dataset (시계열 회귀용)
# ===============================
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y):
        """
        X: (num_samples, time_steps, features)
        y: (num_samples, 1)
        """
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# ===============================
# 2. 모델 정의
# ===============================
class RNNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, rnn_type="RNN", num_layers=1):
        super().__init__()
        if rnn_type == "RNN":
            self.rnn = nn.RNN(input_dim, hidden_dim, num_layers, batch_first=True)
        elif rnn_type == "LSTM":
            self.rnn = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        elif rnn_type == "GRU":
            self.rnn = nn.GRU(input_dim, hidden_dim, num_layers, batch_first=True)
        else:
            raise ValueError("Unsupported rnn_type")

        self.fc = nn.Linear(hidden_dim, 1)  # 회귀 출력

    def forward(self, x):
        out, _ = self.rnn(x)  # out: (batch, time, hidden)
        out = out[:, -1, :]   # 마지막 타임스텝
        out = self.fc(out)
        return out


# --- Transformer Encoder 기반 모델 ---
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                             (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]


class TransformerRegressor(nn.Module):
    def __init__(self, input_dim, model_dim=64, nhead=4, num_layers=2, dropout=0.1):
        super().__init__()
        self.input_fc = nn.Linear(input_dim, model_dim)
        self.pos_encoder = PositionalEncoding(model_dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=model_dim, nhead=nhead, dim_feedforward=128, dropout=dropout
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(model_dim, 1)

    def forward(self, x):
        # x: (batch, time, input_dim)
        x = self.input_fc(x)      # (batch, time, model_dim)
        x = self.pos_encoder(x)   # (batch, time, model_dim)
        x = x.transpose(0, 1)     # (time, batch, model_dim)
        out = self.transformer_encoder(x)
        out = out.mean(dim=0)     # (batch, model_dim)
        out = self.fc(out)
        return out


# ===============================
# 3. 성능 평가 함수
# ===============================
def evaluate(model, dataloader):
    model.eval()
    preds, targets = [], []
    with torch.no_grad():
        for X_batch, y_batch in dataloader:
            pred = model(X_batch)
            preds.append(pred.numpy())
            targets.append(y_batch.numpy())
    preds = np.vstack(preds)
    targets = np.vstack(targets)

    mae = np.mean(np.abs(preds - targets))
    rmse = np.sqrt(np.mean((preds - targets) ** 2))
    mape = np.mean(np.abs((preds - targets) / (targets + 1e-8))) * 100
    return mae, rmse, mape


# ===============================
# 4. 학습 루프
# ===============================
def train_model(model, train_loader, test_loader, criterion, optimizer, epochs=20):
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for X_batch, y_batch in train_loader:
            pred = model(X_batch)
            loss = criterion(pred, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        if (epoch+1) % 5 == 0:  # 5 epoch마다 평가
            mae, rmse, mape = evaluate(model, test_loader)
            print(f"Epoch {epoch+1}/{epochs}, "
                  f"Train Loss: {epoch_loss/len(train_loader):.4f}, "
                  f"MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%")
    return model


# ===============================
# 5. 실행 예시
# ===============================
if __name__ == "__main__":
    # 가짜 데이터 (1000개 샘플, 10타임스텝, feature=5)
    X = np.random.randn(1000, 10, 5)
    y = np.random.randn(1000, 1)

    # train/test split
    split = int(0.8 * len(X))
    train_dataset = TimeSeriesDataset(X[:split], y[:split])
    test_dataset = TimeSeriesDataset(X[split:], y[split:])
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    input_dim = X.shape[2]
    hidden_dim = 32

    # ---- SimpleRNN ----
    print("\n=== SimpleRNN ===")
    rnn_model = RNNModel(input_dim, hidden_dim, rnn_type="RNN")
    train_model(rnn_model, train_loader, test_loader, nn.MSELoss(),
                torch.optim.Adam(rnn_model.parameters(), lr=1e-3))

    # ---- LSTM ----
    print("\n=== LSTM ===")
    lstm_model = RNNModel(input_dim, hidden_dim, rnn_type="LSTM")
    train_model(lstm_model, train_loader, test_loader, nn.MSELoss(),
                torch.optim.Adam(lstm_model.parameters(), lr=1e-3))

    # ---- GRU ----
    print("\n=== GRU ===")
    gru_model = RNNModel(input_dim, hidden_dim, rnn_type="GRU")
    train_model(gru_model, train_loader, test_loader, nn.MSELoss(),
                torch.optim.Adam(gru_model.parameters(), lr=1e-3))

    # ---- Transformer ----
    print("\n=== Transformer Encoder ===")
    trans_model = TransformerRegressor(input_dim, model_dim=64, nhead=4, num_layers=2)
    train_model(trans_model, train_loader, test_loader, nn.MSELoss(),
                torch.optim.Adam(trans_model.parameters(), lr=1e-3))
