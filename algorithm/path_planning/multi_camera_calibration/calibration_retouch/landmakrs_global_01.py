# mm 단위로 설정함

import json, numpy as np

# 경로 설정
ba_path  = "algorithm/path_planning/multi_camera_calibration/outputs/bundle_adjustment/ba_points.json"
out_json = "algorithm/path_planning/multi_camera_calibration/input_files/landmarks_global.json"

# 여기에 A,B,C의 실제 ID를 적으세요
idA, idB, idC = 0, 1, 4  # 예시

# 1) BA 읽기
ba = json.load(open(ba_path))
ids_ba = np.array(ba["ids"])
P_ba   = np.array(ba["points_3d"], float)  # Nx3

def pick(i):
    idx = np.where(ids_ba == i)[0]
    assert len(idx) == 1, f"ID {i} not found or duplicated in BA points."
    return P_ba[idx[0]]

A = pick(idA)
B = pick(idB)
C = pick(idC)

# 2) 목표 전역(mm) 좌표 설정
Q_targets = {
    idA: np.array([  0.0,   0.0, 0.0]),
    idB: np.array([190.0,   0.0, 0.0]),
    idC: np.array([  0.0, 190.0, 0.0]),
}

P = np.stack([A, B, C], axis=0)                           # (3,3) BA
Q = np.stack([Q_targets[idA], Q_targets[idB], Q_targets[idC]], axis=0)  # (3,3) mm

# 3) Umeyama(유사변환: s,R,t) 추정 (최소자승)
def umeyama(P, Q):
    muP, muQ = P.mean(0), Q.mean(0)
    X, Y = P - muP, Q - muQ
    C = (X.T @ Y) / len(P)
    U, D, Vt = np.linalg.svd(C)
    S = np.eye(3); S[-1,-1] = np.sign(np.linalg.det(U @ Vt))
    R = U @ S @ Vt
    # (P-muP) * s*R ≈ (Q-muQ)  → s = tr(D*S) / ||P-muP||^2
    s = np.trace(np.diag(D) @ S) / np.sum((P - muP)**2)
    t = muQ - s * (R @ muP)
    return s, R, t

s, R, t = umeyama(P, Q)

# 4) 전체 점 변환 → 전역(mm)
P_global = (s * (P_ba @ R.T)) + t  # Nx3

# 5) landmarks_global.json 저장
out = {"landmarks_global": P_global.tolist(), "ids": ids_ba.tolist()}
json.dump(out, open(out_json, "w"), indent=2)

# 6) 품질 확인 (A,B,C가 어디로 갔는지)
A2 = (s * (A @ R.T)) + t
B2 = (s * (B @ R.T)) + t
C2 = (s * (C @ R.T)) + t
print("A->", A2, " (target [0,0,0])")
print("B->", B2, " (target [190,0,0])")
print("C->", C2, " (target [0,190,0])")
print(f"Saved {out_json} with {len(ids_ba)} points in mm.")
