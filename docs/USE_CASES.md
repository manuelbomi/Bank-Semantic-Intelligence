# Role-based prompts and realistic workflows

All commands below use fabricated records. Role authorization is illustrative, not production authentication.

## Human resources: training compliance
`python -m bank_semantic ask --role hr --question 'What is our training completion rate?'`
Expected: governed aggregate, HR source citation. Analysts are blocked from HR metrics.

## CEO: mortgage-lender partnership
`python -m bank_semantic ask --role executive --question 'Should we explore a mortgage lender partnership?'`
Expected: count of consented synthetic interest signals, NOT customer identities or lending decisions. Next steps: market analysis, compliance/legal review, fair lending review, contract and consent controls.

## Risk: international transfer alerts
`python -m bank_semantic ask --role fraud --question 'What is the international alert rate?'`
Expected: alert rate and source citations. A rule-triggered alert is not proof of fraud.

## Mobile customer: account overview
`python -m bank_semantic ask --role customer --customer-id 42 --question 'Show my accounts'`
Expected: only synthetic accounts for the authenticated demonstration ID. No balance is fabricated.

## Mobile customer: help center
`python -m bank_semantic ask --role customer --customer-id 42 --question 'How do I reset my mobile password?'`
Expected: public FAQ answer with document citation.

## Analyst: bank-wide KPIs
`python -m bank_semantic ask --role analyst --question 'What are customer KPIs and transaction volume?'`
Expected: consistent governed metrics. No raw PII exposed.

## Developer: graph troubleshooting
Load Neo4j, then run Cypher from `docs/CYPHER.md`. The system does not allow free-form Cypher submitted through the user prompt endpoint.

## Audit company: evidence traceability
Follow a synthetic `Transaction -> FraudAlert` edge, inspect the source FK and alert disposition, and distinguish a rule trigger from an investigated conclusion. Production audit trails require immutable event logs, timestamps, reviewer identity and source hashes.

## Customer service: reviews and complaints
Use review text ingestion to identify app usability complaints. Unstructured claims remain candidates, require consent, and must not be transformed into verified identity or credit signals.

## Operations: service quality
Build aggregate review themes by period. Avoid using a raw text sentiment model as a definitive measure of customer satisfaction; evaluate and audit the taxonomy.

## Data engineering: schema and CDC
Read `sql/schema.sql` and `docs/PRODUCTION.md`. Define source contracts, Delta CDF replay windows, tombstones and idempotent graph updates.
