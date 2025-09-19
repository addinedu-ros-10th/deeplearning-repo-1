Datasets REST API Interface Specification

Base URL
- Production behind Nginx: http(s)://<host>/api/v1
- Direct Uvicorn (local): http://localhost:8000/api/v1

Resource
- Path: /datasets
- Entity fields:
  - dataset_id (UUID)
  - name (string)
  - version (string)
  - storage_path (string/URI)
  - description? (string)
  - creator_name?/creator_email? (string)
  - source_url?/license? (string)
  - class_schema (object; e.g. {"labels":["normal","warning","fall"]})
  - tags (string[])
  - created_at (ISO8601)

Endpoints
1) List datasets
- GET /datasets?skip=0&limit=100
- Response 200: [DatasetResponse]

2) Get dataset by id
- GET /datasets/{dataset_id}
- Response 200: DatasetResponse
- 404 when not found

3) Filter by name
- GET /datasets/name/{name}?skip=0&limit=100

4) Filter by tag
- GET /datasets/tag/{tag}?skip=0&limit=100

5) Create dataset
- POST /datasets
- Body (DatasetCreateRequest):
{
  "name": "AIHub_Fall",
  "version": "v1",
  "storage_path": "s3://bucket/path",
  "description": "Description text",
  "creator_name": "Alice",
  "creator_email": "alice@example.com",
  "source_url": "https://example.com",
  "license": "CC-BY",
  "class_schema": {"labels": ["normal","warning","fall"]},
  "tags": ["fall","pose"]
}
- Response 201: DatasetResponse
- 400 on validation error

6) Update dataset
- PUT /datasets/{dataset_id}
- Body (DatasetUpdateRequest): any subset of create fields
- Response 200: DatasetResponse
- 404 when not found

7) Delete dataset
- DELETE /datasets/{dataset_id}
- Response 204 empty
- 404 when not found

Examples
- List first page
GET {BASE_URL}/datasets?skip=0&limit=20

- Create
POST {BASE_URL}/datasets
Content-Type: application/json
{ "name":"demo","version":"v1","storage_path":"file:///data/demo","class_schema":{"labels":["normal","warning","fall"]},"tags":["demo"] }

References
- Use GET /datasets to obtain dataset_id for other resources (e.g., experiments filtered by dataset).

