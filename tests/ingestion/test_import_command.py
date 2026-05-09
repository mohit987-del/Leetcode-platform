import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from apps.problems.models import Problem, ProblemStarterCode, ProblemTag, ProblemTestCase


class ImportProblemsCommandTests(TestCase):
    def test_import_command_creates_and_updates_problem_bundle(self):
        bundle = {
            "problem": {
                "slug": "two-sum",
                "title": "Two Sum",
                "difficulty": "easy",
                "statement_html": "<p>Find two numbers.</p>",
                "constraints_md": "- n >= 2",
            },
            "tags": ["arrays", "hash-map"],
            "examples": [
                {
                    "input_text": "nums = [2,7,11,15], target = 9",
                    "output_text": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9.",
                }
            ],
            "starter_code": [
                {
                    "language": "python",
                    "template_code": "class Solution:\n    def twoSum(self, nums, target):\n        pass\n",
                }
            ],
            "public_test_cases": [
                {"input_data": "1 2", "expected_output": "3", "weight": 1}
            ],
            "hidden_test_cases": [
                {"input_data": "2 3", "expected_output": "5", "weight": 1}
            ],
            "source": {
                "source_name": "seed",
                "source_url": "https://example.com/two-sum",
                "source_problem_id": "1",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            import_path = Path(temp_dir) / "problems.json"
            import_path.write_text(json.dumps([bundle]), encoding="utf-8")

            call_command("import_problems", str(import_path))

            bundle["problem"]["title"] = "Two Sum Updated"
            import_path.write_text(json.dumps([bundle]), encoding="utf-8")
            call_command("import_problems", str(import_path))

        problem = Problem.objects.get(slug="two-sum")
        self.assertEqual(problem.title, "Two Sum Updated")
        self.assertEqual(ProblemTag.objects.count(), 2)
        self.assertEqual(ProblemStarterCode.objects.count(), 1)
        self.assertEqual(ProblemTestCase.objects.count(), 2)
