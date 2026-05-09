from django.conf import settings
from django.db import models

from apps.problems.models import Problem, ProblemTestCase


class Submission(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Verdict(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        WRONG_ANSWER = "wrong_answer", "Wrong Answer"
        COMPILE_ERROR = "compile_error", "Compile Error"
        RUNTIME_ERROR = "runtime_error", "Runtime Error"
        TIME_LIMIT_EXCEEDED = "time_limit_exceeded", "Time Limit Exceeded"
        MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded", "Memory Limit Exceeded"
        INTERNAL_ERROR = "internal_error", "Internal Error"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="submissions")
    language = models.CharField(max_length=30)
    source_code = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    verdict = models.CharField(max_length=32, choices=Verdict.choices, default=Verdict.PENDING)
    runtime_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_kb = models.PositiveIntegerField(null=True, blank=True)
    compile_output = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]


class SubmissionResult(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="results")
    test_case = models.ForeignKey(ProblemTestCase, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=32)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    runtime_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_kb = models.PositiveIntegerField(null=True, blank=True)


class ProblemAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="problem_attempts")
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="attempts")
    attempt_count = models.PositiveIntegerField(default=0)
    solved = models.BooleanField(default=False)
    first_solved_at = models.DateTimeField(null=True, blank=True)
    last_attempted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "problem")
