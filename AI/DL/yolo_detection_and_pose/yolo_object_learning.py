from ultralytics import YOLO

model = YOLO("yolo11n.pt")

results = model.train(data = "coco128_dl_project.yaml", epochs = 100, imgsz = 640)