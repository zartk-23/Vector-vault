# Final Project Report

## Implemented

FastAPI API, user authentication, workspaces with owner/member roles, collections, secure key creation/revocation, guarded PDF/TXT/Markdown upload, checksum deduplication, synchronous ingestion, chunking, local deterministic embeddings, local VectorStore, tenant-scoped search, grounded fallback answers, Docker, CI skeleton, sample data, evaluation fixture, docs, and tests.

## Configurable integrations

`PineconeVectorStore` and `OpenAIEmbeddingProvider` are implemented behind interfaces and activated through `VECTOR_STORE=pinecone`, Pinecone credentials/index, and `EMBEDDING_PROVIDER=openai`, respectively. This project does not claim a live cloud integration test because credentials were not supplied.

## Not implemented

Redis distributed rate limiting/cache, OpenAI answer generation, asynchronous jobs, persistent object storage, audit/usage tables, API-key authentication middleware, and complete Next.js dashboard flows are intentionally deferred rather than misrepresented.

## Verification

Run `pytest` and `ruff check .` locally. No performance numbers are reported because no benchmark was executed.

## Priorities

P0: production migrations, Pinecone/OpenAI adapters, durable ingestion queue. P1: Redis rate limiter, metrics endpoint, API-key middleware. P2: audit trails, member management UI, reranking and evaluation automation.
