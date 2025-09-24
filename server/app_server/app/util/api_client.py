"""
Simple REST API client for the App Server

Requirements:
- requests (pip install requests)

Usage:
1) Set BASE_URL to the API root (behind Nginx or Uvicorn):
   BASE_URL = "http://localhost/api/v1"  # Nginx
   # or
   BASE_URL = "http://localhost:8000/api/v1"  # Direct

2) Use provided helpers to call endpoints. Each method returns (status_code, json|text).

3) References:
   - Datasets API returns dataset_id (UUID) used by Experiments API
   - Experiments API returns experiment_id (UUID) used by FramePredictions and DetectionEvents
   - FramePredictions uses client-provided session_id (UUID) to group a run

Example:
    client = AppApiClient(base_url="http://localhost:8000/api/v1")
    # Create dataset
    code, data = client.create_dataset({
        "name":"demo","version":"v1","storage_path":"file:///data/demo",
        "class_schema": {"labels":["normal","warning","fall"]},
        "tags":["demo"]
    })
    assert code == 201
    dataset_id = data["dataset_id"]

    # Create experiment
    code, exp = client.create_experiment({
        "name":"exp-lstm-v1","dataset_id":dataset_id,
        "model_path":"s3://bucket/model.pt","framework":"pytorch"
    })
    experiment_id = exp["experiment_id"]

    # Insert a frame prediction
    import uuid
    session_id = str(uuid.uuid4())
    code, fp = client.create_frame_prediction({
        "session_id":session_id,
        "experiment_id":experiment_id,
        "input_uri":"file:///video.mp4",
        "frame_index":0,
        "probabilities":{"normal":1.0},
        "label_pred":"normal"
    })
    assert code == 201

    # Query events (empty expected initially)
    code, events = client.list_detection_events(params={"session_id":session_id})
    print(code, events)
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
import requests


class AppApiClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        if not base_url.endswith("/api/v1"):
            # Allow passing root; append /api/v1 automatically if needed
            if base_url.rstrip("/").endswith("/api"):
                base_url = base_url.rstrip("/") + "/v1"
            elif not base_url.rstrip("/").endswith("/api/v1"):
                base_url = base_url.rstrip("/") + "/api/v1"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ---------- Datasets ----------
    def list_datasets(self, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        return self._get("/datasets", params=params)

    def get_dataset(self, dataset_id: str) -> Tuple[int, Any]:
        return self._get(f"/datasets/{dataset_id}")

    def create_dataset(self, payload: Dict[str, Any]) -> Tuple[int, Any]:
        return self._post("/datasets", json=payload)

    def update_dataset(self, dataset_id: str, payload: Dict[str, Any]) -> Tuple[int, Any]:
        return self._put(f"/datasets/{dataset_id}", json=payload)

    def delete_dataset(self, dataset_id: str) -> Tuple[int, Any]:
        return self._delete(f"/datasets/{dataset_id}")

    # ---------- Experiments ----------
    def list_experiments(self, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        return self._get("/experiments", params=params)

    def get_experiment(self, experiment_id: str) -> Tuple[int, Any]:
        return self._get(f"/experiments/{experiment_id}")

    def list_experiments_by_dataset(self, dataset_id: str, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        path = f"/experiments/dataset/{dataset_id}"
        return self._get(path, params=params)

    def create_experiment(self, payload: Dict[str, Any]) -> Tuple[int, Any]:
        return self._post("/experiments", json=payload)

    def update_experiment(self, experiment_id: str, payload: Dict[str, Any]) -> Tuple[int, Any]:
        return self._put(f"/experiments/{experiment_id}", json=payload)

    def delete_experiment(self, experiment_id: str) -> Tuple[int, Any]:
        return self._delete(f"/experiments/{experiment_id}")

    # ---------- Frame Predictions ----------
    def list_frame_predictions(self, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        return self._get("/frame-predictions", params=params)

    def get_frame_prediction(self, frame_pred_id: int) -> Tuple[int, Any]:
        return self._get(f"/frame-predictions/{frame_pred_id}")

    def create_frame_prediction(self, payload: Dict[str, Any]) -> Tuple[int, Any]:
        return self._post("/frame-predictions", json=payload)

    def create_frame_predictions_batch(self, items: list[Dict[str, Any]]) -> Tuple[int, Any]:
        return self._post("/frame-predictions/batch", json={"items": items})

    def delete_frame_prediction(self, frame_pred_id: int) -> Tuple[int, Any]:
        return self._delete(f"/frame-predictions/{frame_pred_id}")

    # ---------- Detection Events ----------
    def list_detection_events(self, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        return self._get("/detection-events", params=params)

    def get_detection_event(self, event_id: str) -> Tuple[int, Any]:
        return self._get(f"/detection-events/{event_id}")

    def create_detection_event(self, payload: Dict[str, Any]) -> Tuple[int, Any]:
        return self._post("/detection-events", json=payload)

    def delete_detection_event(self, event_id: str) -> Tuple[int, Any]:
        return self._delete(f"/detection-events/{event_id}")

    # ---------- Low-level HTTP helpers ----------
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        url = self.base_url + path
        r = requests.get(url, params=params, timeout=self.timeout)
        return self._resp(r)

    def _post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        url = self.base_url + path
        r = requests.post(url, json=json, timeout=self.timeout)
        return self._resp(r)

    def _put(self, path: str, json: Optional[Dict[str, Any]] = None) -> Tuple[int, Any]:
        url = self.base_url + path
        r = requests.put(url, json=json, timeout=self.timeout)
        return self._resp(r)

    def _delete(self, path: str) -> Tuple[int, Any]:
        url = self.base_url + path
        r = requests.delete(url, timeout=self.timeout)
        return self._resp(r)

    @staticmethod
    def _resp(r: requests.Response) -> Tuple[int, Any]:
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, r.text


if __name__ == "__main__":
    # Quick manual test (adjust BASE_URL as needed)
    client = AppApiClient(base_url="http://localhost:8000/api/v1")
    print(client.list_datasets(params={"skip":0, "limit":5}))

