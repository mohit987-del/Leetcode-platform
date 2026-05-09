from django.db.models import Prefetch
from django.views.generic import DetailView, ListView

from apps.submissions.models import ProblemAttempt

from .models import Problem, ProblemStarterCode


class ProblemListView(ListView):
    model = Problem
    template_name = "problems/list.html"
    context_object_name = "problems"
    paginate_by = 20

    def get_queryset(self):
        queryset = Problem.objects.filter(is_published=True).prefetch_related("tags")
        difficulty = self.request.GET.get("difficulty")
        search = self.request.GET.get("q")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if search:
            queryset = queryset.filter(title__icontains=search)
        return queryset


class ProblemDetailView(DetailView):
    model = Problem
    template_name = "problems/detail.html"
    context_object_name = "problem"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Problem.objects.filter(is_published=True)
            .prefetch_related("tags", "examples", "test_cases")
            .prefetch_related(Prefetch("starter_code", queryset=ProblemStarterCode.objects.order_by("language")))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["starter_code"] = self.object.starter_code.first()
        context["public_test_cases"] = self.object.test_cases.filter(is_public=True)
        attempt = None
        if self.request.user.is_authenticated:
            attempt = ProblemAttempt.objects.filter(user=self.request.user, problem=self.object).first()
        context["attempt"] = attempt
        return context

# Create your views here.
