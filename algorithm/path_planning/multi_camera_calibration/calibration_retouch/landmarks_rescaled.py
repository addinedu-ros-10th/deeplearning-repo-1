# intrinsics에서 사용한 사진과 extrinsics에서 사용한 사진 해상도 차이로 인해 보정 

import json

LM_IN  = "algorithm/path_planning/multi_camera_calibration/input_files/landmarks.json"
LM_OUT = "algorithm/path_planning/multi_camera_calibration/input_files/landmarks_scaled.json"
TARGET = {
    "cam51": {"H0":481, "W0":641, "H1":959, "W1":1279},
    "cam52": {"H0":483, "W0":640, "H1":959, "W1":1279},
    "cam53": {"H0":481, "W0":641, "H1":959, "W1":1279},
    "cam54": {"H0":481, "W0":639, "H1":959, "W1":1279},
}

lm = json.load(open(LM_IN,"r"))
for cam, t in TARGET.items():
    if cam not in lm: continue
    sx = t["W1"] / float(t["W0"]); sy = t["H1"] / float(t["H0"])
    node = lm[cam]
    if isinstance(node, dict) and "points" in node:
        node["points"] = [[p[0]*sx, p[1]*sy] for p in node["points"]]
    elif isinstance(node, list) and node and isinstance(node[0], (list,tuple)):
        lm[cam] = [[p[0]*sx, p[1]*sy] for p in node]
    else:
        print(f"[WARN] {cam}: landmarks 구조 미확인 → 수동 확인 권장")

json.dump(lm, open(LM_OUT,"w"), indent=2)
print(f"Saved: {LM_OUT}")
