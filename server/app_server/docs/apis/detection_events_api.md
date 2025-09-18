Detection Events REST API Interface Specification

Base URL
- http(s)://<host>/api/v1

Resource
- Path: /detection-events
- Fields:
  - event_id (UUID)
  - session_id (UUID)
  - experiment_id (UUID)
  - input_uri (string/URI)
  - start_frame/end_frame (int)
  - start_ts_ms?/end_ts_ms? (int)
  - event_type (string)
  - top_label ("normal"|"warning"|"fall")
  - max_confidence? (0..1)
  - agg_prob? (object)
  - threshold_name?/threshold_snapshot (string/object)
  - trigger_reason? (string)
  - created_at (ISO8601)

Endpoints
1) List
- GET /detection-events?session_id=&experiment_id=&input_uri=&event_type=&top_label=&start_ts_ms_from=&start_ts_ms_to=&skip=0&limit=100

2) Get by id
- GET /detection-events/{event_id}

3) Create
- POST /detection-events
Body (DetectionEventCreateRequest):
{
  "session_id":"<uuid>",
  "experiment_id":"<uuid>",
  "input_uri":"file:///video.mp4",
  "start_frame":120,
  "end_frame":150,
  "event_type":"fall_detected",
  "top_label":"fall",
  "threshold_snapshot": {"rule":"default_v1","fall_thresh":0.6},
  "max_confidence":0.83,
  "agg_prob":{"fall":0.7}
}

4) Delete
- DELETE /detection-events/{event_id}

Examples
- Query by session and time window
GET {BASE_URL}/detection-events?session_id={uuid}&start_ts_ms_from=0&start_ts_ms_to=60000

References
- event_id is UUID returned from create; obtain experiment_id via Experiments, session_id is provided by client per run.

