from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, View

from apps.judge_client.tasks import submit_code_for_judging
from apps.problems.models import Problem

from .forms import SubmissionForm
from .models import Submission


class SubmissionCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        problem = get_object_or_404(Problem, slug=slug, is_published=True)
        form = SubmissionForm(request.POST)
        if not form.is_valid():
            return redirect(problem.get_absolute_url())
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            language=form.cleaned_data["language"],
            source_code=form.cleaned_data["source_code"],
            status=Submission.Status.QUEUED,
            verdict=Submission.Verdict.PENDING,
        )
        submit_code_for_judging.delay(submission.id)
        return redirect(problem.get_absolute_url())


class SubmissionStatusView(LoginRequiredMixin, TemplateView):
    template_name = "submissions/status_card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = get_object_or_404(Submission, pk=kwargs["submission_id"])
        if submission.user != self.request.user:
            raise PermissionError("Not allowed")
        context["submission"] = submission
        return context

    def render_to_response(self, context, **response_kwargs):
        if "submission" not in context:
            return HttpResponseForbidden()
        return super().render_to_response(context, **response_kwargs)


class SubmissionListView(LoginRequiredMixin, ListView):
    template_name = "submissions/list.html"
    context_object_name = "submissions"

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).select_related("problem")

# Create your views here.
