from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.judge_client.tasks import submit_code_for_judging
from apps.problems.models import Problem, ProblemTestCase
from apps.submissions.models import ProblemAttempt, Submission, SubmissionResult


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class JudgeTaskTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="judge-user",
            email="judge@example.com",
            password="strong-password-123",
        )
        self.problem = Problem.objects.create(
            slug="sum",
            title="Sum",
            difficulty=Problem.Difficulty.EASY,
            statement_html="<p>Add numbers.</p>",
            constraints_md="- n <= 10",
            is_published=True,
            source_name="seed",
        )
        self.test_case = ProblemTestCase.objects.create(
            problem=self.problem,
            input_data="1 2",
            expected_output="3",
            is_public=False,
            order=1,
            weight=1,
        )
        self.submission = Submission.objects.create(
            user=self.user,
            problem=self.problem,
            language="python",
            source_code="print(sum(map(int, input().split())))",
        )

    @patch("apps.judge_client.tasks.run_submission")
    def test_task_updates_submission_and_attempts_on_success(self, run_submission_mock):
        run_submission_mock.return_value = {
            "submission_id": self.submission.id,
            "status": "finished",
            "verdict": "accepted",
            "runtime_ms": 12,
            "memory_kb": 2048,
            "compile_output": "",
            "case_results": [
                {
                    "test_case_id": self.test_case.id,
                    "status": "accepted",
                    "stdout": "3",
                    "stderr": "",
                    "runtime_ms": 12,
                    "memory_kb": 2048,
                }
            ],
        }

        submit_code_for_judging(self.submission.id)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.COMPLETED)
        self.assertEqual(self.submission.verdict, Submission.Verdict.ACCEPTED)
        self.assertEqual(SubmissionResult.objects.count(), 1)
        attempt = ProblemAttempt.objects.get(user=self.user, problem=self.problem)
        self.assertTrue(attempt.solved)

    @patch("apps.judge_client.tasks.run_submission")
    def test_task_marks_internal_error_when_judge_fails(self, run_submission_mock):
        run_submission_mock.side_effect = RuntimeError("judge unavailable")

        submit_code_for_judging(self.submission.id)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, Submission.Status.FAILED)
        self.assertEqual(self.submission.verdict, Submission.Verdict.INTERNAL_ERROR)
