# Security policy

Dry-run mode is the default. Apply mode requires HTTPS and reads the API token
only from `CISO_ASSISTANT_TOKEN`; tokens are never written into import plans.

Before production use:

- validate endpoints and payloads against the target instance's live API schema;
- grant a least-privilege Personal Access Token;
- restrict source IPs as recommended by the target platform;
- test in a disposable domain and perimeter;
- implement lookup-before-create idempotent upserts;
- redact secrets, personal data and raw prompts;
- require approval for risk, control, exception and finding state changes.

Report vulnerabilities privately without including live tokens or customer data.
