# API Guide

All routes begin `/api/v1`. Register with `POST /auth/register`, then send `Authorization: Bearer <access token>`. Create a workspace, then collection, upload using multipart `POST /documents/upload?workspace_id=...&collection_id=...`, and call `POST /search` or `/query` with `workspace_id`, `query`, optional `collection_id`, `top_k` (1-20), and filters.

Errors use `{ "error": { "code", "message", "request_id" } }`; `X-Request-ID` is also returned. OpenAPI is available at `/docs`. API key routes are owner-only and only return a raw key from creation.
