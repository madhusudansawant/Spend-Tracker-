from calendar import monthrange
from datetime import date

from django.db.models import Sum

from .models import Expense


def get_month_range(year, month):
    """
    Return the first and last date of a given month.
    """

    start_date = date(year, month, 1)

    last_day = monthrange(year, month)[1]

    end_date = date(year, month, last_day)

    return start_date, end_date


def get_previous_month(year, month):
    """
    Return the previous month and year.
    """

    if month == 1:
        return year - 1, 12

    return year, month - 1


def get_month_summary(user, year, month):
    """
    Calculate monthly spending summary for a user.
    """

    # =====================================================
    # CURRENT MONTH
    # =====================================================

    start_date, end_date = get_month_range(
        year,
        month,
    )

    current_expenses = Expense.objects.filter(
        user=user,
        date__range=[start_date, end_date],
    )

    total_spend = (
        current_expenses.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    category_data = (
        current_expenses
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )


    # =====================================================
    # PREVIOUS MONTH
    # =====================================================

    previous_year, previous_month = get_previous_month(
        year,
        month,
    )

    previous_start, previous_end = get_month_range(
        previous_year,
        previous_month,
    )

    previous_expenses = Expense.objects.filter(
        user=user,
        date__range=[
            previous_start,
            previous_end,
        ],
    )

    previous_total = (
        previous_expenses.aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )


    # =====================================================
    # MONTH-OVER-MONTH CHANGE
    # =====================================================

    if previous_total == 0:

        # Cannot calculate a real percentage
        # from zero using the normal formula.

        month_over_month_change = 0

        if total_spend > 0:
            month_over_month_status = "no_previous_spending"
        else:
            month_over_month_status = "unchanged"

    else:

        month_over_month_change = round(
            float(
                (
                    (total_spend - previous_total)
                    / previous_total
                ) * 100
            )
        )

        if month_over_month_change > 0:
            month_over_month_status = "increased"

        elif month_over_month_change < 0:
            month_over_month_status = "decreased"

        else:
            month_over_month_status = "unchanged"


    # =====================================================
    # CURRENT CATEGORY DATA
    # =====================================================

    current_categories = {
        item["category"]: item["total"]
        for item in category_data
    }


    # =====================================================
    # PREVIOUS CATEGORY DATA
    # =====================================================

    previous_category_data = (
        previous_expenses
        .values("category")
        .annotate(total=Sum("amount"))
    )

    previous_categories = {
        item["category"]: item["total"]
        for item in previous_category_data
    }


    # =====================================================
    # CATEGORY INSIGHTS
    # =====================================================

    category_insights = []

    for category, current_total in current_categories.items():

        previous_category_total = previous_categories.get(
            category,
            0,
        )

        # Cannot calculate percentage
        # when previous category spending is zero.

        if previous_category_total == 0:
            continue

        category_change = (
            (
                current_total
                - previous_category_total
            )
            / previous_category_total
        ) * 100

        category_change = round(
            float(category_change),
            2,
        )

        if category_change > 20:

            category_insights.append(
                {
                    "category": category,
                    "previous_month_spend": (
                        previous_category_total
                    ),
                    "current_month_spend": (
                        current_total
                    ),
                    "percentage_increase": (
                        category_change
                    ),
                    "message": (
                        f"{category} spending increased "
                        f"by {category_change}% "
                        f"compared with last month."
                    ),
                }
            )


    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "year": year,
        "month": month,

        "total_spend": total_spend,

        "spend_by_category": list(
            category_data
        ),

        "previous_month_total": previous_total,

        "month_over_month_change": (
            month_over_month_change
        ),

        "month_over_month_status": (
            month_over_month_status
        ),

        "category_insights": (
            category_insights
        ),
    }

