from django.urls import path

from .views import (
    ExpenseListCreateView,
    SummaryView,
)


urlpatterns = [
    path(
        "expenses/",
        ExpenseListCreateView.as_view(),
        name="expense-list-create",
    ),

    path(
        "summary/",
        SummaryView.as_view(),
        name="summary",
    ),
]