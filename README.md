# CISO Assistant AI Agent Security Connector

**Independent open-source connector for AI agent security evidence, AgentProof
passports, AgentReady production-readiness benchmarks, GRC findings, security
KPIs, and unit economics.**

The connector converts AI-agent assurance output into a neutral, idempotent
import plan intended for mapping to CISO Assistant assets, evidence, findings,
metrics and remediation workflows.

> **Maturity:** v0.1 is a dry-run-first integration contract. It does not include
> CISO Assistant source code and has not been endorsed by Intuitem. Apply-mode
> payloads must be validated against the API schema and permissions of the target
> instance before production use.

## Why this exists

GRC systems manage risks, controls, assessments and evidence. AI-agent security
and SRE tools produce runtime results. This connector preserves the boundary:

```text
AgentProof / AgentReady / future runtime adapters
                       |
             neutral import plan
                       |
          target-version API adapter
                       |
      assets, evidence, findings and metrics
```

It does not send every security alert to GRC. It transports material assurance
results, failed hard gates, accepted evidence and decision-grade KPIs.

## Five-minute dry run

AgentReady:

```bash
python -m ca_agent_connector.cli \
  examples/agentready-result.json \
  --output agentready-import-plan.json
```

AgentProof:

```bash
python -m ca_agent_connector.cli \
  examples/agentproof-result.json \
  --output agentproof-import-plan.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Safety and provenance

- Dry run is the default.
- Apply mode requires HTTPS.
- Tokens come from environment variables and are excluded from plans.
- Stable external references support idempotent upsert implementations.
- Synthetic evidence retains its classification.
- Failed hard gates become findings rather than being hidden by aggregate scores.
- Framework mappings are not certification.

## Apply-mode contract

```bash
export CISO_ASSISTANT_API_URL="https://your-instance.example/api/"
export CISO_ASSISTANT_TOKEN="use-a-least-privilege-token"

ca-agent-connector result.json --apply
```

Apply mode is intentionally marked experimental in v0.1. The exact serializer
fields and endpoint availability may vary by CISO Assistant version and edition.
Use dry run, inspect the live schema, and validate in a disposable environment
first.

## Documentation

- [Object mapping](docs/OBJECT_MAPPING.md)
- [KPIs and unit economics](docs/KPIS_AND_UNIT_ECONOMICS.md)
- [Licensing boundary](docs/LICENSING.md)
- [Security policy](SECURITY.md)

## Roadmap

1. Version-pinned API discovery and schema validation.
2. Lookup-before-create idempotent upserts.
3. AgentReady framework and metric library pack.
4. AgentProof, Kubernetes AI SRE, Wazuh and OpenSearch adapters.
5. Approval-gated finding, exception and remediation workflows.
6. Evidence attachment upload with integrity verification.
7. Contract tests against a disposable community-edition instance.
8. Focused upstream contributions for evidence provenance.

## Independence and trademarks

This is an independent community connector. CISO Assistant and Intuitem are names
of their respective project and organization. No affiliation or endorsement is
claimed.

## License

Apache-2.0. See [LICENSING.md](docs/LICENSING.md) for the integration boundary.
