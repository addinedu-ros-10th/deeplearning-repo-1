Experiments REST API Interface Specification

Base URL
- http(s)://<host>/api/v1

Resource
- Path: /experiments
- Fields:
  - experiment_id (UUID)
  - name (string)
  - dataset_id (UUID)
  - model_path (string/URI)
  - framework?/code_version? (string)
  - params?/metrics? (object)
  - created_at (ISO8601)

Endpoints
1) List
- GET /experiments?skip=0&limit=100

2) Get by id
- GET /experiments/{experiment_id}

3) List by dataset
- GET /experiments/dataset/{dataset_id}?skip=0&limit=100

4) Create
- POST /experiments
Body (ExperimentCreateRequest):
{
  "name":"exp-lstm-v1",
  "dataset_id":"<UUID-of-dataset>",
  "model_path":"s3://bucket/models/model.pt",
  "framework":"pytorch",
  "code_version":"abc123",
  "params": {"epochs":100,"lr":0.001},
  "metrics": {"val_acc":0.9}
}

5) Update
- PUT /experiments/{experiment_id}
Body (ExperimentUpdateRequest): partial fields

6) Delete
- DELETE /experiments/{experiment_id}

Examples
- List by dataset
GET {BASE_URL}/experiments/dataset/{dataset_id}?skip=0&limit=50

References
- Obtain dataset_id via Datasets API first. Use experiment_id to relate predictions/events.

