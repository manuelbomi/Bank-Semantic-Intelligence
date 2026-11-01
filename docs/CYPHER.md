# Cypher cookbook (run after loading Neo4j)

## Customer accounts
```cypher
MATCH (c:Customer {id:'C42'})-[:OWNS]->(a:Account)
RETURN c.id, a.id, a.account_type;
```

## Alerted transactions and their accounts
```cypher
MATCH (c:Customer)-[:OWNS]->(a:Account)-[:HAS_TRANSACTION]->(t:Transaction)
      -[:TRIGGERED_ALERT]->(f:FraudAlert)
RETURN c.id, a.id, t.id, t.country, f.rule LIMIT 25;
```

## Potential mortgage interest (NOT eligibility)
```cypher
MATCH (c:Customer)-[r:INTEREST_SIGNAL]->(p:Product {name:'mortgage'})
RETURN c.id, r.status, r.evidence LIMIT 20;
```

## Review-derived unverified topics
```cypher
MATCH (r:Review)-[e:MENTIONS_CANDIDATE]->(t:Topic)
WHERE e.status = 'unverified'
RETURN r.id, t.name, e.evidence LIMIT 20;
```

## Graph quality: missing source evidence
```cypher
MATCH ()-[r]->() WHERE r.evidence IS NULL
RETURN type(r), count(r);
```

## Relationship distribution
```cypher
MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY count(r) DESC;
```

**Security:** Never allow a public LLM to generate arbitrary Cypher against a privileged Neo4j connection. Use reviewed templates, allowlists, parameters, scoped identities, query limits and read-only service accounts.
