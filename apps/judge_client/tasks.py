from celery import shared_task
from django.utils import timezone

from apps.problems.models import ProblemTestCase
from apps.submissions.models import ProblemAttempt, Submission, SubmissionResult

from .client import run_submission


def _build_submission_payload(submission):
    test_cases = [
        {
            "id": test_case.id,
            "input_data": test_case.input_data,
            "expected_output": test_case.expected_output,
            "is_public": test_case.is_public,
            "weight": test_case.weight,
        }
        for test_case in submission.problem.test_cases.order_by("order")
    ]
    return {
        "submission_id": submission.id,
        "language": submission.language,
        "source_code": submission.source_code,
        "test_cases": test_cases,
        "limits": {"timeout_seconds": 2, "memory_mb": 128},
    }


def _update_attempt(submission):
    attempt, _ = ProblemAttempt.objects.get_or_create(user=submission.user, problem=submission.problem)
    attempt.attempt_count += 1
    attempt.last_attempted_at = timezone.now()
    if submission.verdict == Submission.Verdict.ACCEPTED:
        attempt.solved = True
        if attempt.first_solved_at is None:
            attempt.first_solved_at = timezone.now()
    attempt.save()


@shared_task(queue="submissions")
def submit_code_for_judging(submission_id):
    submission = Submission.objects.select_related("problem", "user").get(pk=submission_id)
    submission.status = Submission.Status.RUNNING
    submission.save(update_fields=["status"])
    try:
        payload = _build_submission_payload(submission)
        result = run_submission(payload)
    except Exception as exc:
        submission.status = Submission.Status.FAILED
        submission.verdict = Submission.Verdict.INTERNAL_ERROR
        submission.compile_output = str(exc)
        submission.finished_at = timezone.now()
        submission.save(update_fields=["status", "verdict", "compile_output", "finished_at"])
        _update_attempt(submission)
        return

    submission.results.all().delete()
    for case_result in result.get("case_results", []):
        test_case = ProblemTestCase.objects.filter(pk=case_result.get("test_case_id")).first()
        SubmissionResult.objects.create(
            submission=submission,
            test_case=test_case,
            status=case_result["status"],
            stdout=case_result.get("stdout", ""),
            stderr=case_result.get("stderr", ""),
            runtime_ms=case_result.get("runtime_ms"),
            memory_kb=case_result.get("memory_kb"),
        )

    submission.status = Submission.Status.COMPLETED if result.get("verdict") != Submission.Verdict.INTERNAL_ERROR else Submission.Status.FAILED
    submission.verdict = result.get("verdict", Submission.Verdict.INTERNAL_ERROR)
    submission.runtime_ms = result.get("runtime_ms")
    submission.memory_kb = result.get("memory_kb")
    submission.compile_output = result.get("compile_output", "")
    submission.finished_at = timezone.now()
    submission.save(
        update_fields=[
            "status",
            "verdict",
            "runtime_ms",
            "memory_kb",
            "compile_output",
            "finished_at",
        ]
    )
    _update_attempt(submission)
