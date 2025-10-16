'''
# 1 ==============================
yolo detection 한거 calibration 적용해서 matrix 형태로 넣기


# 2 ============================

occupancy grid map 그리기 -> 완료


# 3 ================================
A* algorithm 적용하기 -> 완료


'''

from typing import List, Tuple, Callable
import math
import heapq

import matplotlib.pyplot as plt
import numpy as np

from ultralytics import YOLO
import os, csv
import cv2

import json


# folder create ================================================
path_output_dir = "PersonA/PathPlanning_outputs/TC02_outputs/path_outputs"
os.makedirs(path_output_dir, exist_ok = True)

Homography_output_dir = "PersonA/PathPlanning_outputs/TC02_outputs/Homography_outputs"
os.makedirs(Homography_output_dir, exist_ok = True)

YOLO_output_dir = "PersonA/PathPlanning_outputs/TC02_outputs/YOLO_outputs"
os.makedirs(YOLO_output_dir, exist_ok = True)


# yolo detection  ==================================================================================================================


print(" ")
print(" ======================================= ")
print("  1️⃣ YOLO Detection saved to CSV ")
print(" ======================================= ")
print(" ")

# TC 01
# cam_frames = {
#    "cam51" : "PersonA/Test_frames/TC01/cam_no_1.png",
#    "cam52" : "PersonA/Test_frames/TC01/cam_no_2.png",
#    "cam53" : "PersonA/Test_frames/TC01/cam_no_3.png",
#    "cam54" : "PersonA/Test_frames/TC01/cam_no_4.png"
# }

# TC 02
cam_frames = {
   "cam51" : "PersonA/Test_frames/TC02/TC02_cam51.png",
   "cam52" : "PersonA/Test_frames/TC02/TC02_cam52.png",
   "cam53" : "PersonA/Test_frames/TC02/TC02_cam53.png",
   "cam54" : "PersonA/Test_frames/TC02/TC02_cam54.png"
}

# TC 03
# cam_frames = {
#    "cam51" : "PersonA/Test_frames/TC03/TC03_cam51.png",
#    "cam52" : "PersonA/Test_frames/TC03/TC03_cam52.png",
#    "cam53" : "PersonA/Test_frames/TC03/TC03_cam53.png",
#    "cam54" : "PersonA/Test_frames/TC03/TC03_cam54.png"
# }

model = YOLO("yolov10n.pt")

# cvs에 박스 좌표 저장
csv_path = "PersonA/PathPlanning_outputs/TC02_outputs/YOLO_outputs/detections_xyxy.csv"
with open(csv_path, "w", newline="") as f :
    writer = csv.writer(f)

    # (x1, y1) = 왼쪽 위 / (x2, y2) = 오른쪽 아래
    writer.writerow(["image_key", "class_id", "class_name", "conf", "x1", "y1", "x2", "y2"])

    res_per_cam = {}

    for key, img_path in cam_frames.items() :
        result = model.predict(img_path, verbose = False)[0]

        res_per_cam[key] = result

        annotated = result.plot()
        out_img_path = f"PersonA/PathPlanning_outputs/TC02_outputs/YOLO_outputs/TC02_{key}_annotated.png"
        cv2.imwrite(out_img_path, annotated)

        if result.boxes is None or len(result.boxes) == 0 :
            print(f"[INFO] {key} : no detections")
            continue
        
        H, W = result.orig_shape # box의 크기 정의해주는거임
        xyxy = result.boxes.xyxy.cpu().numpy()
        cls = result.boxes.cls.cpu().numpy()
        conf = result.boxes.conf.cpu().numpy()
        # top-left 기준으로 자표 잡음

        for i in range(len(xyxy)) :
            c_id = int(cls[i])
            c_nm = model.names.get(c_id, str(c_id))

            if c_nm.lower() == "person" :
                continue

            x1, y1, x2, y2 = xyxy[i]

            x_left_bottom, y_left_bottom = float(x1), float(y2)
            x_right_bottom, y_right_bottom = float(x2), float(y2)

            writer.writerow([key, c_id, c_nm, float(conf[i]), float(x1), float(y1), float(x2), float(y2)])

        print(f" ✅ {key}: saved {out_img_path}, detections={len(xyxy)}")

print(f"[DONE] CSV saved -> {csv_path}")





# csv에 이미지 픽셀 좌표계 기준 저장됨
# 픽셀 좌표계 -> world 좌표계 (Homography 적용)


# Homography 계산 ==============================================================================================



print(" ")
print(" ======================================= ")
print(" 2️⃣ Homography ")
print(" ======================================= ")
print(" ")


INTRINSICS_JSON = "PersonA/input_files/intrinsics_scaled.json" # K, dist
GLOBAL_POSES_JSON = "PersonA/outputs/global_registration/global_poses.json" # R, T

# JSON 가져오기
with open(INTRINSICS_JSON, "r") as f :
    intr = json.load(f)

with open(GLOBAL_POSES_JSON, "r") as f :
    extr = json.load(f)


# K, R, t 가져오기

def get_K(cam) :
    K = np.array(intr[cam]["K"], dtype=np.float64)
    return K


def get_Rt_world_to_camera(cam) :
    item = extr[cam]
    R = np.array(item["R"], dtype = np.float64)
    t = np.array(item["t"], dtype = np.float64).reshape(3,1)
    return R, t


# H_i2w가 image 2 World

def compute_H_i2w(K, R, t) :
    r1 = R[:, 0:1]
    r2 = R[:, 1:2]
    H_w2i = K @ np.hstack([ r1,  r2,  t ])
    H_i2w = np.linalg.inv(H_w2i)
    return H_i2w


# 호모그래피 결과 저장
H_i2w_per_cam = {}
for cam in ["cam51", "cam52", "cam53", "cam54"] :
    K = np.array(intr[cam]["K"], dtype = np.float64)
    R, t = get_Rt_world_to_camera(cam)
    H_i2w_per_cam[cam] = compute_H_i2w(K, R, t)

# Json 파일로 저장
H_dict = {cam: H_i2w_per_cam[cam].tolist() for cam in H_i2w_per_cam}
with open("PersonA/PathPlanning_outputs/TC02_outputs/Homography_outputs/H_iw2.json", "w") as f :
    json.dump(H_dict, f, indent=2)

print("homography cam51 : ", H_i2w_per_cam["cam51"])
print("homography cam52 : ", H_i2w_per_cam["cam52"])
print("homography cam53 : ", H_i2w_per_cam["cam53"])
print("homography cam54 : ", H_i2w_per_cam["cam54"])

print(" ")
print(" 📌 Saved in 'PersonA/PathPlanning_outputs/TC02_outputs/Homography_outputs' ")
print(" ")

# Grid와 월드 좌표계 원점 불일치 해결하기 ==============================================================================================


'''
이 부분이 개빡
'''


GRID_CFG = {
    "ORIGIN_W": np.array([2700, 6300], dtype=float), 
    "RES_MM": 450.0,            
    # "ALIGN_THETA_DEG": 5.0, # 월드가 그리드에 비해 CCW +5도 틀어졌다면
    "Y_DOWN": True,   # row가 아래로 증가하도록 Y 뒤집기  <- matrix랑 맞춰주는 거임
    "X_MIRROR" : True,
    "ROWS": 24,
    "COLS": 10,
}


# 실제 좌표를 matrix grid에서의 위치로 투영시키는것 (원점ㅇ이 동일하지 않아서 해야되는 부분임 )
def world_to_grid(X_mm, Y_mm, cfg) :
    
    # 1) 원점 이동
    px = X_mm - cfg["ORIGIN_W"][0]
    py = Y_mm - cfg["ORIGIN_W"][1]

    # 2) 회전 보정 (월드를 -theta만큼 회전시켜 그리드 축에 정렬)
    # th = math.radians(cfg["ALIGN_THETA_DEG"])
    # c, s = math.cos(-th), math.sin(-th)
    # xr = c * px - s * py
    # yr = s * px + c * py

    xr = px
    yr = py

    # 3) 아래로 증가하는 row 맞추기
    if cfg["Y_DOWN"]:
        yr = -yr
    
    if cfg.get("X_MIRROR", False) :
        xr = -xr

    # 4) mm → 셀 인덱스
    col = int(math.floor(xr / cfg["RES_MM"]))
    row = int(math.floor(yr / cfg["RES_MM"]))

    # 5) 범위 검사
    if 0 <= row < cfg["ROWS"] and 0 <= col < cfg["COLS"]:
        return row, col
    return None

def pixel_to_world_mm(cam, px, py) :
    H = H_i2w_per_cam[cam]
    pt = np.array([[[px, py]]], dtype=np.float32)
    out = cv2.perspectiveTransform(pt, H)
    return float(out[0,0,0]), float(out[0,0,1])

def stamp_obstacle(matrix, row, col, pad_cells=0):
    """셀 (row,col)과 주변 pad_cells 반경을 장애물로 표시"""
    h, w = len(matrix), len(matrix[0])
    for dr in range(-pad_cells, pad_cells+1):
        for dc in range(-pad_cells, pad_cells+1):
            rr, cc = row+dr, col+dc
            if 0 <= rr < h and 0 <= cc < w:
                matrix[rr][cc] = False  # 장애물



# 경로 생성 알고리즘 =====================================================================================================================


print(" ")
print(" ======================================= ")
print(" 3️⃣ Path Planning ")  #4️⃣
print(" ======================================= ")
print(" ")


# 대각선 방향 이동을 포함한 경우 ( 방향 벡터 )
d_col = (-1, 0, 1, -1, 1, -1, 0, 1)
d_row = (-1, -1, -1, 0, 0, 1, 1, 1)

Coord = Tuple[int, int] 


def a_star(matrix, start, dest) -> Tuple[int, List[Coord]]:
    global d_row
    global d_col

    h = len(matrix)
    w = len(matrix[0])

    # H 테이블
    heuristic_cost = [[float("inf")] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            if matrix[i][j]:
                heuristic_cost[i][j] = get_octile_distance((i, j), dest)

    # G 테이블
    g_cost = [[float("inf")] * w for _ in range(h)]
    sy, sx = start
    g_cost[sy][sx] = 0.0

    # 경로 복원
    came_from: dict[Coord, Coord] = {}

    # 방문 처리
    closed = [[False] * w for _ in range(h)]

    # 힙: (f, y, x)
    heap = []
    heapq.heappush(heap, (heuristic_cost[sy][sx], sy, sx))

    while heap:
        f, y, x = heapq.heappop(heap)

        # 이미 더 좋은 경로로 확정된 경우 스킵
        if closed[y][x]:
            continue
        closed[y][x] = True

        # 도착 확인
        if (y, x) == dest:
            break

        # 8방향 이웃
        for k in range(8):
            ny = y + d_row[k]
            nx = x + d_col[k]
            if not is_valid(matrix, closed, ny, nx):
                continue

            # 스텝 비용: 직선=1, 대각=루트2
            dy = abs(ny - y)
            dx = abs(nx - x)
            step = math.sqrt(2) if (dx == 1 and dy == 1) else 1.0

            tentative_g = g_cost[y][x] + step
            if tentative_g < g_cost[ny][nx]:
                g_cost[ny][nx] = tentative_g
                came_from[(ny, nx)] = (y, x)
                f_new = tentative_g + heuristic_cost[ny][nx]
                heapq.heappush(heap, (f_new, ny, nx))

    # 도달 실패 처리
    gy, gx = dest
    if g_cost[gy][gx] == float("inf"):
        return math.inf, [], closed, heuristic_cost

    # 경로 복원
    path: List[Coord] = []
    cur = dest
    while cur != start:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()

    total_cost = g_cost[gy][gx]
    return total_cost, path, closed, heuristic_cost


def get_octile_distance(pq1, pq2) :
    y1, x1 = pq1
    y2, x2 = pq2
    dx = abs(x1 - x2)
    dy = abs(y1 - y2)
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)


def is_valid( matrix, vis, row, col) :
    h = len(matrix)
    w = len(matrix[0])

    if not (0 <= row < h and 0 <= col < w) :
        return False
    
    if not matrix[row][col] :
        return False
    
    if vis[row][col] :
        return False
    
    return True


# def _print_cost(matrix) :
#     h = len(matrix)
#     w = len(matrix[0])

#     print(" - Heuristic Cost - ")
#     for i in range(h) :
#         for j in range(w) :
#             print("." if math.isinf(matrix[i][j]) else matrix[i][j], end= " ")
#         print()
#     print()

# def _print_path(matrix, start, dest, title) :
#     h = len(matrix)
#     w = len(matrix[0])

#     print(f" ---- {title} ---- ")
#     for i in range(h) :
#         for j in range(w) :
#             if (i, j) == start:
#                 print("S", end =" ")
#             elif (i, j) == dest :
#                 print("G", end = " ")
#             else : 
#                 print("O" if matrix[i][j] else ".", end= " ")
#         print()
#     print()

_print_shortest_distance: Callable[
    [ Coord, Coord, int], None
] = lambda start, dest, total_cost : print(f"{start} -> {dest} 최단거리 : {total_cost}")


def _print_shortest_path(matrix, paths, start, dest) :
    h = len(matrix)
    w = len(matrix[0])

    canvas = [["."] * w for _ in range(h)]

    # 시작 / 도착 표시
    sy, sx = start
    gy, gx = dest
    canvas[sy][sx] = "S"
    canvas[gy][gx] = "G"

    # 화살표 그리기
    prev_y, prev_x = start
    for cur_y, cur_x in paths :
        dy = cur_y - prev_y
        dx = cur_x - prev_x

        # 시작/도착은 화살표로 덮지 않음
        if (cur_y, cur_x) != start and (cur_y, cur_x) != dest:
            if dy == 1 and dx == 0:
                canvas[cur_y][cur_x] = "↓" 
            elif dy == -1 and dx == 0:
                canvas[cur_y][cur_x] = "↑" 
            elif dy == 0 and dx == 1:
                canvas[cur_y][cur_x] = "→"
            elif dy == 0 and dx == -1:
                canvas[cur_y][cur_x] = "←"
            elif dy == 1 and dx == 1:
                canvas[cur_y][cur_x] = "↘" 
            elif dy == 1 and dx == -1:
                canvas[cur_y][cur_x] = "↙" 
            elif dy == -1 and dx == 1:
                canvas[cur_y][cur_x] = "↗"
            elif dy == -1 and dx == -1:
                canvas[cur_y][cur_x] = "↖"        

        prev_y, prev_x = cur_y, cur_x
    print(" -- Shortest Path -- ")
    for i in range(h) :
        for j in range(w) :
            # 장애물 있는 칸은 1로 출력되도록 함
            if not matrix[i][j] and canvas[i][j] == "." :
                print("1", end= " ")
            else:
                print(canvas[i][j], end= " ")
        print()
    print()

def _plot_grid_result(matrix, paths, start, dest) :
    h = len(matrix) 
    w = len(matrix[0])

    # 0 = 빈칸 / 1 = 장애물
    grid = np.zeros((h,w))
    for i in range(h) :
        for j in range(w) :
            if not matrix[i][j] :
                grid[i, j] = 1

    # 경로 2
    for (y, x) in paths :
        grid[y, x] = 2

    # 시작 S와 도착 G는 3, 4로 표시
    sy, sx = start
    gy, gx = dest
    grid[sy, sx] = 3
    grid[gy, gx] = 4

    # 색상 맵핑 정의 (0 ~ 4)
    cmap = plt.get_cmap("Accent", 5)

    plt.figure(figsize=(w * 0.6, h * 0.6))
    plt.imshow(grid, cmap = cmap, origin="upper")

    import matplotlib.patches as mpatches
    legend_elements = [
        mpatches.Patch(color=cmap(0), label = "Free (True)"),
        mpatches.Patch(color=cmap(1), label = "Obstacle (False)"),
        mpatches.Patch(color=cmap(2), label = "Path"),
        mpatches.Patch(color=cmap(3), label = "Start"),
        mpatches.Patch(color=cmap(4), label = "Goal"),
    ]
    plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc = "upper left")

    plt.title("A* Path Planning Result")
    plt.xlabel("X (columns)")
    plt.ylabel("Y (rows)")

    # plt.grid(True, linewidth=0.3, color="gray", alpha=0.5)
    ax = plt.gca()

    ax.set_xticks(np.arange(-.5, w, 1), minor = True)
    ax.set_yticks(np.arange(-.5, h, 1), minor = True)

    ax.set_xticks(np.arange(0, w, 1))
    ax.set_yticks(np.arange(0, h, 1))

    plt.grid(which="minor", color="black", linestyle="-", linewidth=0.5)
    plt.savefig("PersonA/PathPlanning_outputs/TC02_outputs/path_outputs/final_astar_result.png", dpi = 300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__" :

    # occupancy grid 설정하는 부분임 ========================================================================================

    rows, cols = 24, 10

    matrix = [[True for _ in range(cols)] for _ in range(rows)]

    '''
    장애물 위치 하드코딩한 부분임 -> 추후 수정

    # False = 장애물 O
    # True = 장애물 X

    '''
    
    # for i in range(15, 20) :
    #     for j in range(0, 4) :
    #         matrix[i][j] = False

    # for i in range(3, 10) :
    #     for j in range(3,10) :
    #         matrix[i][j] = False


    '''
    장애물 위치 좌표계 기반으로 설정
    '''
    
    for cam, res in res_per_cam.items():
        if not res.boxes or len(res.boxes) == 0:
            print(f"[INFO] {cam} : no detections")
            continue
        xyxy = res.boxes.xyxy.cpu().numpy()
        for (x1, y1, x2, y2) in xyxy:
            # 박스 아래 중앙 픽셀
            px = (x1 + x2) / 2.0
            py = y2
            print(f"[PIXEL] cam={cam} px,py =({px: .1f}, {py:.1f})")


            # 픽셀 → 월드(mm)
            X_mm, Y_mm = pixel_to_world_mm(cam, px, py)
            print(f"[WORLD[mm] X,Y = ({X_mm:.1f}, {Y_mm:.1f})")

            # 월드(mm) → grid 인덱스
            rc = world_to_grid(X_mm, Y_mm, GRID_CFG)
            if rc is None:
                print("  └─ [OUT] 그리드 범위 밖 (찍지 않음)")
                continue
            row, col = rc
            print(f"[GRID] row,col=({row}, {col})  (stamp)")

            # 장애물 표시 (필요시 pad_cells로 두께 줌)
            stamp_obstacle(matrix, row, col, pad_cells=1)
    

    # =================================================================================================================================
    
    start = (23, 0)
    dest = (0, 5)
    total_cost, paths, vis, heuristic_cost = a_star(matrix, start, dest)

    # _print_path(matrix, start, dest, "Path")
    # _print_cost(heuristic_cost)
    # _print_path(vis, start, dest, "Visited")
    _print_shortest_distance(start, dest, total_cost)
    print (" ")
    _print_shortest_path(matrix, paths, start, dest)
    _plot_grid_result(matrix, paths, start, dest)

    plt.close()

    print(" ")
    print(" 📌 Saved in 'PersonA/PathPlanning_outputs/TC02_outputs/path_outputs/final_astar_result.png' ")
    print(" ")



    total_cost, paths, vis, heuristic_cost = a_star(matrix, start, dest)

    # ✅ 경로 CSV 저장
    path_csv_path = "PersonA/PathPlanning_outputs/TC02_outputs/path_outputs/final_path.csv"

    with open(path_csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "row", "col"])  # 헤더
        for idx, (r, c) in enumerate(paths):
            writer.writerow([idx, r, c])

    print(f"📁 경로 CSV 저장 완료 → {path_csv_path}")


    # ✅ 경로 JSON 저장
    path_json_path = "PersonA/PathPlanning_outputs/TC02_outputs/path_outputs/final_path.json"

    path_dict = {
        "total_cost": total_cost,
        "start": start,
        "goal": dest,
        "path": [{"row": r, "col": c} for (r, c) in paths]
    }

    with open(path_json_path, "w") as f:
        json.dump(path_dict, f, indent=2)

    print(f"📁 경로 JSON 저장 완료 → {path_json_path}")







