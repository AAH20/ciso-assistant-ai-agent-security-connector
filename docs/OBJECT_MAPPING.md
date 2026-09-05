# Object mapping

The connector uses an intermediate import plan so normalization can be tested
without access to a CISO Assistant instance. API payloads are an adapter boundary
and must be validated against the target instance's live schema.

| Assurance source | Neutral object | Intended CISO Assistant object |
|---|---|---|
| Agent identity | `asset` | Asset |
| Full evaluation result | `evidence` | Evidence |
| Failed control or hard gate | `finding` | Finding |
| KPI definition | `metric_definition` | Metric definition |
| KPI observation | `metric_sample` | Metric sample |
| Accepted failure | future `risk_acceptance` | Risk acceptance |
| Temporary bypass | future `exception` | Security exception |
| Required remediation | future `task` | Task |
| AgentReady profile | future library | Compliance framework |

## Idempotency

External references derive from the source format, agent identity, version,
result hash, object type, and metric/check key. Replaying the same result produces
the same references. The target-specific adapter must resolve by external
reference before deciding whether to create or update an object.

## Provenance

Every imported run preserves:

- source format and version;
- result hash;
- evidence classification;
- generation timestamp;
- agent name and version;
- stable run reference;
- limitations and mapping version.

Synthetic inputs must never be upgraded to `observed` during import.
