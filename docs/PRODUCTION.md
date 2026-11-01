# Production-readiness roadmap and explicit gaps

This repository is an executable **reference implementation**, not a production bank platform. Do not connect actual customer data or expose its demo API to the internet.

## P0 — demonstrable now
- Deterministic synthetic bank data, referential graph construction, provenance and source status.
- Minimal PII in graph exports, consent gating for review extraction.
- Central semantic KPI catalog, role-scoped local prompt workflows, document citations.
- Portable offline retrieval and evaluation, unit tests and CI.
- Optional real Delta read/write, Neo4j upsert, Splink candidate scoring, local LLM extraction.

## P1 — essential before sensitive workloads
- OIDC/OAuth2 service auth, ABAC/RBAC with policy engine, row/column/edge-level access controls.
- Proper secrets manager, mTLS, private networks, encryption, audit logs, backups, disaster recovery.
- Source connectors with least-privilege accounts, schema contracts, idempotent batch and CDC.
- Delta Change Data Feed version tracking, replay, deletes, consent withdrawal and graph tombstones.
- Production vector database (e.g. pgvector, OpenSearch, Milvus) and embedding pipelines.
- Hybrid lexical + vector + graph retrieval, tenant-scoped filters, ranking and reranking.
- Calibrated Splink on labeled pairs, review workflow, reversible merges/splits and confidence monitoring.
- Schema-validated LLM extraction, prompt injection defenses, moderation, source-grounded citations.
- Data retention, lineage, model cards, bias/fairness evaluation, consumer privacy review.

## P2 — enterprise scale
- Spark/Databricks jobs, Kafka event streaming, change capture, partitioned Delta storage.
- OpenTelemetry tracing, Prometheus metrics, structured logs and p95/p99 SLOs.
- Load testing, chaos/failure injection, capacity planning, cost budgets and DR drills.
- CI dependency pinning, SBOM, SAST/DAST, secret scanning, signed images and deployment approvals.
- Domain ownership, ontology migration, metric versioning, contract testing and catalog governance.
- Document ACL propagation, temporal graph semantics, attribution and factuality evaluation.
- Human-in-the-loop workflows for fraud investigation and adverse decision safeguards.

## Compliance and sensitive data
- Consider GLBA, applicable privacy laws, FFIEC guidance, data retention, model risk management,
  fair lending and anti-discrimination obligations with counsel/compliance teams.
- Do not use review-derived mortgage interest as a credit decision or share profiles without a
  lawful basis and specific applicable consent.
- Date of birth and address should stay in controlled systems, not in general-purpose graph exports.
- Graph inferences and LLM claims should not be treated as verified evidence without validation.

## Distinguish implemented vs conceptual
- PostgreSQL Compose creates a schema, but the demo does not populate/query PostgreSQL directly.
- Databricks, Spark, Kafka and CDC are architecture targets, not implemented connectors.
- `vector.py` is lexical similarity, NOT a real vector DB or embedding model.
- `assistant.py` is deterministic routing, NOT a fully autonomous agent or generative RAG.
- Optional Splink, Delta, Neo4j and LLM paths require external services/dependencies and have
  not been end-to-end integration tested in this package.
- Demo role headers are forgeable; local API is NOT safe for public deployment.

## Optional concrete adapters added
- `vector_chroma.py`: persistent Chroma + SentenceTransformer embeddings for synthetic public policy retrieval. It is not wired into the core prompt router.
- `postgres_adapter.py`: synthetic PostgreSQL fixture loader, separate from the CSV graph ingestion pipeline.
