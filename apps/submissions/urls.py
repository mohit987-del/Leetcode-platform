from django.urls import path

from .views import SubmissionCreateView, SubmissionListView, SubmissionStatusView

app_name = "submissions"

urlpatterns = [
    path("", SubmissionListView.as_view(), name="list"),
    path("status/<int:submission_id>/", SubmissionStatusView.as_view(), name="status"),
    path("problem/<slug:slug>/submit/", SubmissionCreateView.as_view(), name="create"),
]
