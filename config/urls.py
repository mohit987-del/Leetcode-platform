from django.contrib import admin
from django.urls import include, path

from apps.core.views import LandingPageView

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('admin/', admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("problems/", include("apps.problems.urls")),
    path("submissions/", include("apps.submissions.urls")),
]
