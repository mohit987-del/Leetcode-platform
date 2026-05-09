import os
import unittest

from fastapi.testclient import TestClient

from judge_runner.app import app
from judge_runner.runner import LocalPythonRunner
from judge_runner.schemas import SubmissionRequest


class JudgeRunnerTests(unittest.TestCase):
    def setUp(self):
        self.request = SubmissionRequest(
            submission_id=1,
            language="python",
            source_code="def solve(raw_input):\n    a, b = map(int, raw_input.split())\n    return a + b\n",
            test_cases=[{"id": 1, "input_data": "1 2", "expected_output": "3", "is_public": False, "weight": 1}],
            limits={"timeout_seconds": 1, "memory_mb": 64},
        )

    def test_local_runner_accepts_valid_solution(self):
        result = LocalPythonRunner().run(self.request)

        self.assertEqual(result["verdict"], "accepted")

    def test_local_runner_detects_wrong_answer(self):
        request = self.request.model_copy(update={"source_code": "def solve(raw_input):\n    return 99\n"})

        result = LocalPythonRunner().run(request)

        self.assertEqual(result["verdict"], "wrong_answer")

    def test_local_runner_detects_runtime_error(self):
        request = self.request.model_copy(update={"source_code": "def solve(raw_input):\n    raise ValueError('boom')\n"})

        result = LocalPythonRunner().run(request)

        self.assertEqual(result["verdict"], "runtime_error")

    def test_local_runner_detects_timeout(self):
        request = self.request.model_copy(
            update={"source_code": "def solve(raw_input):\n    while True:\n        pass\n"}
        )

        result = LocalPythonRunner().run(request)

        self.assertEqual(result["verdict"], "time_limit_exceeded")

    def test_api_rejects_missing_token(self):
        client = TestClient(app)

        response = client.post("/internal/judge/submissions/", json=self.request.model_dump())

        self.assertEqual(response.status_code, 401)

    def test_api_accepts_valid_payload(self):
        os.environ["JUDGE_RUNNER_TOKEN"] = "codearena-judge-9x4k2m8p1q"
        client = TestClient(app)

        response = client.post(
            "/internal/judge/submissions/",
            headers={"Authorization": "Bearer test-token"},
            json=self.request.model_dump(),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["verdict"], "accepted")
