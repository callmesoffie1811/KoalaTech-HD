import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPOSITORY_ROOT / ".github" / "workflows"


class ProductionWorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = (WORKFLOWS / "01-ci.yml").read_text()
        cls.staging_deployment = (WORKFLOWS / "02-deploy-staging.yml").read_text()
        cls.staging_test = (WORKFLOWS / "03-staging-test.yml").read_text()
        cls.production = (WORKFLOWS / "04-deploy-production.yml").read_text()
        cls.drift = (WORKFLOWS / "05-drift-detection.yml").read_text()

    def test_ci_runs_the_workflow_contract_suite(self):
        self.assertIn("      - name: Validate workflow contracts", self.ci)
        self.assertIn(
            "run: python3 -m unittest tests/test_workflow_contracts.py -v",
            self.ci,
        )

    def test_each_promotion_requires_its_upstream_workflow_to_succeed(self):
        success_condition = "    if: ${{ github.event.workflow_run.conclusion == 'success' }}"
        self.assertIn(success_condition, self.staging_deployment)
        self.assertIn(success_condition, self.staging_test)
        self.assertIn(success_condition, self.production)

    def test_production_workflow_restores_the_task_9_3c_baseline(self):
        required_fragments = (
            "name: 04 - Deploy to Production",
            '      - "03 - Test Staging"',
            "    if: ${{ github.event.workflow_run.conclusion == 'success' }}",
            "      name: production",
            "          ref: ${{ github.event.workflow_run.head_sha }}",
            "            -f kubernetes/production/",
            "${{ vars.AKS_RESOURCE_GROUP }}",
            "${{ vars.AKS_CLUSTER_NAME }}",
            "${{ vars.ACR_LOGIN_SERVER }}",
            "      - name: Verify production frontend",
        )

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.production)

        self.assertEqual(self.production.count("kubectl set image deployment/"), 6)

    def test_production_calls_drift_detection_after_deployment(self):
        self.assertRegex(
            self.production,
            re.compile(
                r"post-deployment-drift-check:\s+"
                r"name: Post-Deployment Drift Detection\s+"
                r"needs: deploy-production\s+"
                r"uses: \./\.github/workflows/05-drift-detection\.yml",
                re.MULTILINE,
            ),
        )
        self.assertIn("source_sha: ${{ github.event.workflow_run.head_sha }}", self.production)
        self.assertIn("secrets: inherit", self.production)

    def test_drift_workflow_remains_independent_and_becomes_reusable(self):
        required_fragments = (
            "  workflow_dispatch:",
            "  schedule:",
            "  workflow_call:",
            "      source_sha:",
            "          ref: ${{ inputs.source_sha || github.sha }}",
            "if: ${{ inputs.simulate_error }}",
        )

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.drift)

    def test_both_teams_alerts_use_melbourne_time(self):
        timestamp = (
            'DETECTED="$(TZ=Australia/Melbourne '
            "date '+%Y-%m-%d %H:%M:%S %Z')\""
        )
        self.assertEqual(self.drift.count(timestamp), 2)


if __name__ == "__main__":
    unittest.main()
