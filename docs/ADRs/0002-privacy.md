# ADR 0002 — Minimize PII in graph and retrieval
Status: Accepted.
The graph export intentionally excludes email and DOB; customer self-service requires an actor ID.
A production system must enforce trusted identity, policy and deletion propagation server-side.
