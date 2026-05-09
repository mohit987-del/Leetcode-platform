from django.urls import path

from .views import ProblemDetailView, ProblemListView

app_name = "problems"

urlpatterns = [
    path("", ProblemListView.as_view(), name="list"),
    path("<slug:slug>/", ProblemDetailView.as_view(), name="detail"),
]
