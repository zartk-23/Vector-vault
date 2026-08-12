# Security

## Implemented

- Argon2 password hashing; signed, expiring access/refresh JWTs.
- Server-side workspace membership and owner checks.
- SHA-256 API-key storage and a one-time plaintext display.
- Upload size/MIME allowlist; user filenames are not used as paths.
- SQLAlchemy parameterized ORM queries; request IDs; no credential/document-content logging by application code.
- Retrieved content is treated as data. The local fallback does not follow retrieved instructions; an LLM provider must retain this separation in its system prompt.

## Future / recommended

Use virus scanning, object storage, Redis-backed distributed rate limits, key rotation/revocation lists for refresh tokens, CSRF protection if browser-cookie auth is added, secret manager integration, dependency scanning, audit logs, and CSP/HTTPS at the proxy. Prompt injection cannot be perfectly eliminated; constrain tools, isolate tenant context, cite sources, and evaluate adversarial corpora.
