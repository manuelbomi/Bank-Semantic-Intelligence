# Comprehensive tutorial: explore the platform module by module

## Lesson 0: generate a synthetic bank
Run `python -m bank_semantic generate`. Open `data/generated/customers.csv`, `accounts.csv`, `transactions.csv`, `alerts.csv`, `crm_profiles.csv`, `mortgage_signals.csv`, `reviews.jsonl` and `hr_metrics.csv`. All records are fabricated. Money uses cents rather than floating point.

## Lesson 1: relational foundations
Read `sql/schema.sql`. Primary keys uniquely identify rows; foreign keys connect accounts to customers and transactions to accounts. The graph uses those keys as verified-source edges. PostgreSQL in Compose provides a schema demonstration; the portable pipeline reads generated CSV files. Loading and CDC from PostgreSQL remain integration work.

## Lesson 2: Delta Lake and unstructured text
Run `python -m bank_semantic delta-write` after installing `pip install '.[full]'`. This writes a genuine Delta table of customer review text. Then run `python -m bank_semantic demo --delta-path data/delta/reviews`. Delta is a table format, not itself an unstructured database.

## Lesson 3: entity resolution
Read `identity.py`. Exact normalized emails produce proposed links. `splink_candidates` uses Splink 4, DuckDB, Jaro-Winkler, exact email/region, blocking and EM estimation. Run `python -m bank_semantic splink` after optional installation. Inspect candidate probabilities; the small synthetic dataset is not enough for calibration and the Splink path has not been integration-tested. No candidate link is promoted to a canonical identity automatically.

## Lesson 4: extract from review text
Read `extract.py`. Offline mode maps simple text patterns to provisional themes. Optional `--mode llm` calls a trusted OpenAI-compatible local model. Only exact source substrings are accepted as evidence. Even a substring can be misleading (negation, quotation, sarcasm), so status remains unverified.

## Lesson 5: construct a knowledge graph
Read `graph.py` and run `python -m bank_semantic demo`. Inspect `artifacts/graph.json`. Source foreign-key edges are `verified_source`, while review edges are `unverified`. The graph intentionally omits DOB and email, which are sensitive identity attributes not required for the demonstration.

## Lesson 6: Neo4j
Run `docker compose up -d neo4j`, set `BANK_NEO4J_PASSWORD` to the Compose password, then `python -m bank_semantic neo4j-load`. Visit http://localhost:7474. Read `docs/CYPHER.md` for queries. The loader performs upserts but does not handle deletions or consent revocations; do not mistake it for a production CDC sink.

## Lesson 7: document retrieval
Read `vector.py` and `data/policies.json`. The baseline uses lexical cosine similarity, not vector embeddings. Run `python -m bank_semantic ask --role customer --customer-id 1 --question 'How do I reset my mobile password?'`. Role classification filters documents BEFORE search. For true vector retrieval, see `docs/PRODUCTION.md`.

## Lesson 8: governed metrics
Read `semantic.py`. A single metric definition supports executives, risk and analysts. Run `python -m bank_semantic ask --role executive --question 'customer KPI'`. Observe integer-cent transaction volume and explicit denominators for alert rates.

## Lesson 9: authorization and prompt routing
Read `assistant.py`. Try HR, executive, customer and fraud prompts in `docs/USE_CASES.md`. The deterministic router never executes arbitrary model-generated SQL/Cypher. The FastAPI facade is for local demos only and has no real authentication.

## Lesson 10: evaluation
Run `python -m bank_semantic evaluate` and `python -m unittest discover -s tests -v`. Evaluate identity precision/recall, extraction evidence, retrieval recall@k, citation correctness, group leakage, graph consistency and p95 latency before production rollout.

## Exercises
1. Add a `branches` table and a `SERVICED_BY` relationship.
2. Add a dated `Address` entity with verified provenance; avoid inferring residence from reviews.
3. Implement explicit mortgage-interest consent expiry and graph deletion propagation.
4. Create 100 manually labeled identity pairs and calibrate Splink thresholds.
5. Add a vector store adapter with embeddings and hybrid lexical + vector ranking.
6. Add an OpenTelemetry trace for ingestion, retrieval and model inference.
7. Add a review queue for unverified text edges.
8. Add a tenant_id to every entity and enforce it across all graph queries.
9. Write a temporal graph query: accounts that triggered alerts in a date window.
10. Add contract tests between PostgreSQL, Delta and the graph sink.

## Lesson 11: genuine vector similarity
`vector_chroma.py` indexes policy documents with SentenceTransformer embeddings in Chroma. Compare its nearest-neighbor results to the transparent lexical baseline in `vector.py`. The core assistant intentionally remains on the dependency-free baseline; wiring vector results into hybrid retrieval is an extension.

## Lesson 12: PostgreSQL adapter
`postgres_adapter.py` shows parameterized fixture loading into a disposable PostgreSQL schema. Contrast physical relational constraints with graph edges derived from the same keys. A future source adapter should stream SQL query results, not pull an entire banking database into memory.
