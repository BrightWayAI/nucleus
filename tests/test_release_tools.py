from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_connector_report import validate_report  # noqa: E402


class ConnectorReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads((ROOT / "connector-tests" / "plan.json").read_text())

    def valid_report(self) -> dict[str, object]:
        required = {"calendar", "mail", "crm"}
        results = []
        for row in self.plan["connectors"]:
            connector_id = row["id"]
            passing = connector_id in required
            results.append(
                {
                    "id": connector_id,
                    "status": "pass" if passing else "not-run",
                    "tool": f"fixture.{connector_id}.read" if passing else None,
                    "latencyMs": 1 if passing else None,
                    "observation": {
                        "recordCount": 0,
                        "contentTypes": ["structured"],
                        "topLevelKeys": ["items"],
                    }
                    if passing
                    else None,
                    "errorCode": None,
                }
            )
        return {
            "schemaVersion": 1,
            "release": "2026.09.0-rc.1",
            "host": "claude",
            "profile": "operator",
            "runAt": "2026-09-15T12:00:00Z",
            "results": results,
        }

    def test_operator_profile_accepts_metadata_only_live_results(self) -> None:
        self.assertEqual(validate_report(self.plan, self.valid_report()), [])

    def test_required_connector_must_pass(self) -> None:
        report = self.valid_report()
        report["results"][0]["status"] = "skip"
        errors = validate_report(self.plan, report)
        self.assertTrue(any("required connector did not pass: calendar" in item for item in errors))

    def test_raw_connector_payload_fields_are_rejected(self) -> None:
        report = self.valid_report()
        report["results"][0]["content"] = "private connector payload"
        errors = validate_report(self.plan, report)
        self.assertTrue(any("unsupported fields" in item for item in errors))
        self.assertTrue(any("raw-data fields" in item for item in errors))

    def test_release_must_match_when_pinned(self) -> None:
        errors = validate_report(
            self.plan,
            self.valid_report(),
            expected_release="2026.09.1",
        )
        self.assertTrue(any("expected '2026.09.1'" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
