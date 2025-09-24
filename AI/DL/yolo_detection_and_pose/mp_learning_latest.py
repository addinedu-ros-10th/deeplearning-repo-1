import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight

from torch.utils.data import DataLoader, TensorDataset
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

import pandas as pd

"""
============================= 조정할 수 있는 옵션 =============================
 * seg_len : 세그먼트 길이. 학습에 사용될 영상의 기준 길이를 지정. 단위는 프레임.
 * hidden_dim : hidden layer의 차원
 * num_epochs : 에포크 수
 * test_size : 테스트에 사용될 모델의 수
 * 반복 훈련 번호 지정 위치에서 range() 값으로 훈련에 쓰일 csv 파일 범위 설정 가능.
"""

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, num_layers = 3):
        super(LSTMModel, self).__init__()

        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first = True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

def load_data(base_dir, categories, seg_len = 90):

    data = []
    labels = []
    label_map = {category: idx for idx, category in enumerate(categories)}

    
    category_path = os.path.join(base_dir, "coordinate") # 하위 경로 생성

    print(f"checking files in: {category_path}")

    for i in range(1, 800):                                            # 반복 훈련 번호 지정
        file_path = os.path.join(category_path, f"keypoints_{i}.csv") # csv 접근 경로 생성
        print(i)

        if os.path.exists(file_path):
            keypoints_csv = pd.read_csv(file_path)

            keypoints_csv_normal = keypoints_csv[keypoints_csv["label"] == "Normal"]
            keypoints_csv_warning = keypoints_csv[keypoints_csv["label"] == "Warning"]
            keypoints_csv_fall = keypoints_csv[keypoints_csv["label"] == "Fall"]

            keypoints_csv_normal = keypoints_csv_normal.drop(["frame_id","frame_path", "label"], axis = 1)
            keypoints_csv_warning = keypoints_csv_warning.drop(["frame_id","frame_path", "label"], axis = 1)
            keypoints_csv_fall = keypoints_csv_fall.drop(["frame_id","frame_path", "label"], axis = 1)

            keypoints_normal = keypoints_csv_normal.values.tolist() # csv 파일의 vlaue들을 list 형태로 변환
            keypoints_warning = keypoints_csv_warning.values.tolist()
            keypoints_fall = keypoints_csv_fall.values.tolist()

            if len(keypoints_normal) > seg_len:
                keypoints_normal = keypoints_normal[:seg_len]

            elif len(keypoints_normal) < seg_len:
                pad_width_normal = seg_len - len(keypoints_normal)
                keypoints_normal = np.pad(keypoints_normal, ((0, pad_width_normal), (0, 0)), mode = "constant")

            if len(keypoints_warning) > seg_len:
                keypoints_warning = keypoints_warning[:seg_len]

            elif len(keypoints_warning) < seg_len:
                pad_width_warning = seg_len - len(keypoints_warning)
                keypoints_warning = np.pad(keypoints_warning, ((0, pad_width_warning), (0, 0)), mode = "constant")

            if len(keypoints_fall) > seg_len:
                keypoints_fall = keypoints_fall[:seg_len]

            elif len(keypoints_fall) < seg_len:
                pad_width_fall = seg_len - len(keypoints_fall)
                keypoints_fall = np.pad(keypoints_fall, ((0, pad_width_fall), (0, 0)), mode = "constant")

            data.append(keypoints_normal)
            data.append(keypoints_warning)
            data.append(keypoints_fall)

            for category in categories:
                labels.append(label_map[category])
        
        else:
            print(f"file not found: {file_path}")

    return np.array(data), np.array(labels)

def standardize_data(data):

    mean = data.mean(axis = (1, 2), keepdims = True)

    std = data.std(axis = (1, 2), keepdims = True)

    standardized_data = (data - mean) / (std + 1e-8)

    return standardized_data

base_dir = "./"
categories = ["Normal", "Warning", "Fall"]
labels_map = {"Normal": 0, "Warning": 1, "Fall": 2}

X, y = load_data(base_dir, categories)

# print(f"Data shape: {X.shape}, Labels shape: {y.shape}")

X_standardized = standardize_data(X)

X_train, X_temp, y_train, y_temp = train_test_split(X_standardized, y, test_size = 0.2, random_state = 13, stratify = y)

X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size = 0.2, random_state = 13, stratify = y_temp)

# print(f"train shape: {X_train.shape}, validation shape: {X_val.shape}, Test shape: {X_test.shape}")
    
input_dim = X_train.shape[2]
hidden_dim = 256
output_dim = len(labels_map)
model = LSTMModel(input_dim = input_dim, hidden_dim = hidden_dim, output_dim = output_dim)

train_dataset = TensorDataset(torch.tensor(X_train).float(), torch.tensor(y_train).long())
val_dataset = TensorDataset(torch.tensor(X_val).float(), torch.tensor(y_val).long())
train_loader = DataLoader(train_dataset, batch_size = 4, shuffle = True)
val_loader = DataLoader(val_dataset, batch_size = 4)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr = 0.001)

class_weights = compute_class_weight("balanced", classes = np.unique(y_train), y=y_train)
criterion = nn.CrossEntropyLoss(weight = torch.tensor(class_weights, dtype = torch.float))

scheduler = StepLR(optimizer, step_size = 5, gamma = 0.5)

num_epochs = 100

for epoch in range(num_epochs):
    model.train()
    train_loss = 0

    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        X_batch = X_batch.view(X_batch.size(0), -1, input_dim)
        y_pred = model(X_batch)
        loss = criterion(y_pred, y_batch)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    scheduler.step()

    model.eval()
    val_loss = 0

    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch = X_batch.view(X_batch.size(0), -1, input_dim)
            y_pred = model(X_batch)
            val_loss = criterion(y_pred, y_batch).item()

    print(f"Epoch {epoch + 1}/{num_epochs}, Train_Loss: {train_loss / len(train_loader): .4f}, Validation Loss: {val_loss / len(val_loader): .4f}")

model.eval()
y_true, y_pred = [], []

test_loader = DataLoader(TensorDataset(torch.tensor(X_test).float(), torch.tensor(y_test).long()), batch_size = 4)

with torch.no_grad():
    for X_batch, y_batch in test_loader:
        X_batch = X_batch.view(X_batch.size(0), -1, input_dim)

        outputs = model(X_batch)
        _, preds = torch.max(outputs, 1)
        y_true.extend(y_batch.numpy())
        y_pred.extend(preds.numpy())

print(classification_report(y_true, y_pred, target_names = list(labels_map.keys())))

scripted_model = torch.jit.script(model)

output_dir = "./"

model_path = os.path.join(output_dir, "lstm_model_scripted.pt")

scripted_model.save(model_path)
print(f"Scripted model saved to {model_path}")