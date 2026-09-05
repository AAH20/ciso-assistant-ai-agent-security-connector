import json
import tempfile
import unittest
from pathlib import Path

from ca_agent_connector.cli import main
from ca_agent_connector.client import CisoAssistantClient
from ca_agent_connector.normalize import build_import_plan, detect_format


ROOT = Path(__file__).parents[1]


class ConnectorTests(unittest.TestCase):
    def load(self, name):
        return json.loads((ROOT / "examples" / name).read_text())

    def test_agentready_plan_maps_metrics(self):
        plan = build_import_plan(self.load("agentready-result.json"))
        self.assertEqual(plan["source_format"], "agentready")
        self.assertEqual(plan["summary"]["finding_count"], 0)
        self.assertGreater(plan["summary"]["metric_sample_count"], 10)
        self.assertEqual(plan["classification"], "synthetic_controlled_test")

    def test_agentproof_failure_becomes_finding(self):
        plan = build_import_plan(self.load("agentproof-result.json"))
        self.assertEqual(plan["source_format"], "agentproof")
        self.assertEqual(plan["summary"]["finding_count"], 1)
        finding = next(item for item in plan["objects"] if item["kind"] == "finding")
        self.assertIn("Tenant boundary", finding["payload"]["name"])

    def test_stable_idempotency_references(self):
        document = self.load("agentready-result.json")
        first = build_import_plan(document)
        second = build_import_plan(document)
        self.assertEqual(first["run_reference"], second["run_reference"])
        self.assertEqual([x["external_ref"] for x in first["objects"]], [x["external_ref"] for x in second["objects"]])

    def test_unsupported_input_fails(self):
        with self.assertRaises(ValueError):
            detect_format({"unknown": True})

    def test_apply_client_requires_https_and_token(self):
        with self.assertRaises(ValueError):
            CisoAssistantClient("http://localhost/api/", "token")
        with self.assertRaises(ValueError):
            CisoAssistantClient("https://example.invalid/api/", "")

    def test_cli_defaults_to_dry_run(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "plan.json"
            rc = main([str(ROOT / "examples" / "agentready-result.json"), "--output", str(output)])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(output.read_text())["mode"], "dry_run")


if __name__ == "__main__":
    unittest.main()
