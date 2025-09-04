# -*- coding: utf-8 -*-
"""
Ultralytics YOLO 탐지 모듈
- 프레임(np.ndarray, BGR)를 입력받아, 디텍션 리스트(클래스명/신뢰도/바운딩박스) 반환
- 다른 스크립트에서도 쉽게 재사용할 수 있도록 클래스로 캡슐화
"""
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

try:
    from ultralytics import YOLO
except Exception as e:  # ultralytics 미설치 또는 GPU/CUDA 환경 이슈 등
    YOLO = None
    _IMPORT_ERR = e
else:
    _IMPORT_ERR = None


@dataclass
class Detection:
    """단일 탐지 결과 구조체"""
    cls_id: int
    cls_name: str
    conf: float
    x1: int
    y1: int
    x2: int
    y2: int


class YoloDetector:
    """
    Ultralytics YOLO 래퍼
    - model_path: "yolov8n.pt" 같은 가중치 경로 또는 모델명
    - device: "cuda", "cpu" 등 (None 이면 자동 선택)
    - conf_thres: 신뢰도 임계값
    - classes: 특정 클래스만 필터링하려면 정수 ID 리스트 (예: [0] → person만)
    """
    def __init__(self, model_path: str = "yolov8n.pt",
                 device: Optional[str] = None,
                 conf_thres: float = 0.25,
                 classes: Optional[List[int]] = None):
        if YOLO is None:
            raise ImportError(
                f"[YoloDetector] ultralytics 로드 실패: {_IMPORT_ERR}\n"
                "가상환경에서 `pip install ultralytics` 후 다시 시도하세요."
            )
        self.model = YOLO(model_path)
        self.device = device
        self.conf_thres = float(conf_thres)
        self.classes = classes  # None이면 전체 클래스 사용

        # 클래스 인덱스→이름 매핑
        self.class_names = self.model.model.names if hasattr(self.model, 'model') else self.model.names

    def detect(self, frame_bgr: np.ndarray) -> List[Detection]:
        """
        입력 프레임에서 객체 탐지 수행
        - 반환: Detection 리스트
        """
        # predict 인자: imgsz, conf, device 등 필요시 추가
        results = self.model.predict(
            source=frame_bgr,
            conf=self.conf_thres,
            device=self.device,
            verbose=False
        )

        dets: List[Detection] = []
        if not results:
            return dets

        r0 = results[0]
        boxes = getattr(r0, "boxes", None)
        if boxes is None:
            return dets

        xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else boxes.xyxy.numpy()
        conf = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else boxes.conf.numpy()
        cls  = boxes.cls.cpu().numpy()  if hasattr(boxes.cls,  "cpu") else boxes.cls.numpy()

        for (x1, y1, x2, y2), p, c in zip(xyxy, conf, cls):
            c = int(c)
            if self.classes is not None and c not in self.classes:
                continue
            cls_name = self.class_names.get(c, str(c)) if isinstance(self.class_names, dict) else str(c)
            dets.append(Detection(
                cls_id=c,
                cls_name=cls_name,
                conf=float(p),
                x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2)
            ))
        return dets
