from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.problems.models import Problem, ProblemStarterCode, ProblemTestCase
from apps.submissions.models import Submission


class SubmissionFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="submitter",
            email="submitter@example.com",
            password="strong-password-123",
        )
        self.problem = Problem.objects.create(
            slug="two-sum",
            title="Two Sum",
            difficulty=Problem.Difficulty.EASY,
            statement_html="<p>Find two numbers.</p>",
            constraints_md="- n >= 2",
            is_published=True,
            source_name="seed",
        )
        ProblemStarterCode.objects.create(
            problem=self.problem,
            language="python",
            template_code="class Solution:\n    def solve(self):\n        pass\n",
        )
        ProblemTestCase.objects.create(
            problem=self.problem,
            input_data="1 2",
            expected_output="3",
            is_public=True,
            order=1,
            weight=1,
        )

    @patch("apps.submissions.views.submit_code_for_judging.delay")
    def test_authenticated_user_can_create_submission(self, delay_mock):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("submissions:create", kwargs={"slug": self.problem.slug}),
            {"language": "python", "source_code": "print(3)"},
        )

        self.assertEqual(response.status_code, 302)
        submission = Submission.objects.get()
        self.assertEqual(submission.status, Submission.Status.QUEUED)
        delay_mock.assert_called_once_with(submission.id)

    def test_submission_status_partial_renders(self):
        submission = Submission.objects.create(
            user=self.user,
            problem=self.problem,
            language="python",
            source_code="print(3)",
            status=Submission.Status.QUEUED,
            verdict=Submission.Verdict.PENDING,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("submissions:status", kwargs={"submission_id": submission.id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Queued")
