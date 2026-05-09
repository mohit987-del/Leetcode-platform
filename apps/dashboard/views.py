from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.views.generic import TemplateView

from apps.submissions.models import Submission


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submissions = Submission.objects.filter(user=self.request.user).select_related("problem")
        context["recent_submissions"] = submissions[:5]
        context["stats"] = submissions.aggregate(
            solved=Count("id", filter=Q(verdict=Submission.Verdict.ACCEPTED)),
            total=Count("id"),
        )
        return context

# Create your views here.
