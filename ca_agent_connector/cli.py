"""CLI for producing and optionally applying CISO Assistant import plans."""

import argparse
import json
import os
from pathlib import Path

from .client import CisoAssistantClient
from .normalize import build_import_plan


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="ca-agent-connector",
        description="Map AI agent assurance results into a CISO Assistant import plan.",
    )
    parser.add_argument("input", help="AgentProof or AgentReady JSON result")
    parser.add_argument("--output", default="ciso-assistant-import-plan.json")
    parser.add_argument("--apply", action="store_true", help="POST planned objects to a configured API")
    parser.add_argument("--base-url", help="CISO Assistant API base URL ending in /api/")
    args = parser.parse_args(argv)

    document = json.loads(Path(args.input).read_text(encoding="utf-8"))
    plan = build_import_plan(document)
    Path(args.output).write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    if not args.apply:
        print(json.dumps({"mode": "dry_run", "output": args.output, **plan["summary"]}, indent=2))
        return 0

    token = os.environ.get("CISO_ASSISTANT_TOKEN", "")
    base_url = args.base_url or os.environ.get("CISO_ASSISTANT_API_URL", "")
    client = CisoAssistantClient(base_url, token)
    applied = []
    for item in plan["objects"]:
        applied.append({"kind": item["kind"], "response": client.create(item["kind"], item["payload"])})
    print(json.dumps({"mode": "apply", "applied_count": len(applied)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
