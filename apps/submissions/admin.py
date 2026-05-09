from django.contrib import admin

from .models import ProblemAttempt, Submission, SubmissionResult


class SubmissionResultInline(admin.TabularInline):
    model = SubmissionResult
    extra = 0
    readonly_fields = ("status", "stdout", "stderr", "runtime_ms", "memory_kb")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "problem", "language", "status", "verdict", "submitted_at")
    list_filter = ("status", "verdict", "language")
    search_fields = ("user__username", "problem__title")
    inlines = [SubmissionResultInline]


@admin.register(ProblemAttempt)
class ProblemAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "problem", "attempt_count", "solved", "last_attempted_at")
    list_filter = ("solved",)
