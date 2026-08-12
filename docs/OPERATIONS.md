# Operations

Run `docker compose up --build`, apply reviewed Alembic migrations for production, and monitor `/api/v1/health` and `/api/v1/health/ready`. Structured request logs include route, status, latency and request ID. The repository includes Prometheus-compatible dependency but does not yet expose a metrics endpoint; do not claim metric collection until it is wired.

Use environment secrets, explicit CORS origins, managed PostgreSQL/Redis, and Pinecone credentials in deployment. Back up relational metadata; vectors can be reconstructed by re-ingesting retained documents.
