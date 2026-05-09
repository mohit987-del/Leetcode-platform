from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.problems.models import Problem, ProblemExample, ProblemTag
from apps.submissions.models import ProblemAttempt


class ProblemCatalogTests(TestCase):
    def setUp(self):
        self.arrays = ProblemTag.objects.create(name="Arrays", slug="arrays")
        self.easy_problem = Problem.objects.create(
            slug="two-sum",
            title="Two Sum",
            difficulty=Problem.Difficulty.EASY,
            statement_html="<p>Find two numbers.</p>",
            constraints_md="- n >= 2",
            is_published=True,
            source_name="seed",
        )
        self.easy_problem.tags.add(self.arrays)
        ProblemExample.objects.create(
            problem=self.easy_problem,
            input_text="nums = [2,7,11,15], target = 9",
            output_text="[0,1]",
            explanation="Because nums[0] + nums[1] == 9.",
            order=1,
        )
        self.hard_problem = Problem.objects.create(
            slug="hard-graph",
            title="Hard Graph",
            difficulty=Problem.Difficulty.HARD,
            statement_html="<p>Do graph things.</p>",
            constraints_md="- n <= 10^5",
            is_published=True,
            source_name="seed",
        )

    def test_problem_list_filters_by_difficulty(self):
        response = self.client.get(reverse("problems:list"), {"difficulty": Problem.Difficulty.EASY})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Two Sum")
        self.assertNotContains(response, "Hard Graph")

    def test_problem_detail_shows_example(self):
        response = self.client.get(reverse("problems:detail", kwargs={"slug": self.easy_problem.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find two numbers")
        self.assertContains(response, "nums = [2,7,11,15], target = 9")

    def test_problem_detail_shows_solved_status_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="solver",
            email="solver@example.com",
            password="strong-password-123",
        )
        ProblemAttempt.objects.create(
            user=user,
            problem=self.easy_problem,
            attempt_count=1,
            solved=True,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("problems:detail", kwargs={"slug": self.easy_problem.slug}))

        self.assertContains(response, "Solved")
