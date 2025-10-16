# intrinsics에서 사용한 사진과 extrinsics에서 사용한 사진 해상도 차이로 인해 보정 

import json, copy

IN_PATH  = "algorithm/path_planning/multi_camera_calibration/input_files/intrinsics.json"
OUT_PATH = "algorithm/path_planning/multi_camera_calibration/input_files/intrinsics_scaled.json"

# 카메라별 원본(H0,W0) → 목표(H1,W1) = (959,1279)
TARGET = {
    "cam51": {"H0":481, "W0":641, "H1":959, "W1":1279},
    "cam52": {"H0":483, "W0":640, "H1":959, "W1":1279},
    "cam53": {"H0":481, "W0":641, "H1":959, "W1":1279},
    "cam54": {"H0":481, "W0":639, "H1":959, "W1":1279},
}

data = json.load(open(IN_PATH, "r"))
out  = copy.deepcopy(data)

for cam, t in TARGET.items():
    if cam not in out:
        print(f"[WARN] {cam} not in intrinsics.json, skip"); continue
    sx = t["W1"] / float(t["W0"])
    sy = t["H1"] / float(t["H0"])
    K  = out[cam]["K"]
    # K = [[fx, s, cx],[0, fy, cy],[0,0,1]]
    K[0][0] *= sx                 # fx
    K[0][1] *= sx                 # skew s (대부분 0이지만 있으면 sx로 스케일)
    K[0][2] *= sx                 # cx
    K[1][1] *= sy                 # fy
    K[1][2] *= sy                 # cy
    out[cam]["K"] = K
    # image_shape / image_size 갱신
    if "image_shape" in out[cam]:
        out[cam]["image_shape"] = [t["H1"], t["W1"]]
    out[cam]["image_size"] = [t["W1"], t["H1"]]  # 없던 필드라면 추가

    print(f"[OK] {cam}: sx={sx:.9f}, sy={sy:.9f}")

json.dump(out, open(OUT_PATH, "w"), indent=2)
print(f"Saved: {OUT_PATH}")
