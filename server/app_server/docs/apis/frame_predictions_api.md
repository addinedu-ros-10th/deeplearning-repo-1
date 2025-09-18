Frame Predictions REST API Interface Specification

Base URL
- http(s)://<host>/api/v1

Resource
- Path: /frame-predictions
- Fields:
  - frame_pred_id (int)
  - session_id (UUID)
  - experiment_id (UUID)
  - input_uri (string/URI)
  - frame_index (int >=0)
  - ts_rel_ms? (int)
  - label_pred ("normal"|"warning"|"fall")
  - confidence? (0..1)
  - probabilities (object, e.g. {"normal":0.85,"warning":0.08,"fall":0.07})
  - passed? (bool)
  - threshold_name?/threshold_snapshot? (string/object)
  - created_at (ISO8601)

Endpoints
1) List
- GET /frame-predictions?session_id={uuid}&experiment_id={uuid}&input_uri=&label_pred=&frame_index_from=&frame_index_to=&skip=0&limit=100

2) Get by id
- GET /frame-predictions/{frame_pred_id}

3) Create (single)
- POST /frame-predictions
Body:
{
  "session_id":"<uuid>",
  "experiment_id":"<uuid>",
  "input_uri":"file:///video.mp4",
  "frame_index":100,
  "probabilities":{"normal":0.1,"warning":0.2,"fall":0.7},
  "label_pred":"fall",
  "confidence":0.7
}

4) Create (batch)
- POST /frame-predictions/batch
Body: { "items": [ <FramePredictionCreateRequest>, ... ] }

5) Delete
- DELETE /frame-predictions/{frame_pred_id}

Examples
- Batch insert 2 frames
POST {BASE_URL}/frame-predictions/batch
{ "items": [ {"session_id":"...","experiment_id":"...","input_uri":"file:///v.mp4","frame_index":1,"probabilities":{"normal":1},"label_pred":"normal"}, {"session_id":"...","experiment_id":"...","input_uri":"file:///v.mp4","frame_index":2,"probabilities":{"fall":1},"label_pred":"fall"} ] }

References
- Use experiment_id from Experiments API; session_id is client-generated to group one run.

