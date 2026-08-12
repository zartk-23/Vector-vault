# Data Pipeline

`Upload -> validate size/type -> checksum/duplicate check -> extraction -> whitespace normalization -> configurable chunks (900 characters, 150 overlap) -> embedding -> vector upsert -> relational chunk records -> completed`.

The chunk defaults favor moderately focused retrieval with enough overlap to preserve boundary context. Smaller chunks improve precision and cost more; larger chunks improve surrounding context but can dilute relevance. The current synchronous MVP marks failure safely; production should run idempotent, retryable jobs and delete partial vector upserts on failure.
