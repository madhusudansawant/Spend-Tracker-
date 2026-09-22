from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Expense


User = get_user_model()


class ExpenseAPITestCase(APITestCase):

    def setUp(self):
        """
        Runs before every test.
        Creates two users so we can also test user isolation.
        """

        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPassword123"
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123"
        )

        self.expenses_url = "/api/expenses/"
        self.summary_url = "/api/summary/"

        self.client.force_authenticate(
            user=self.user
        )

    # -----------------------------------
    # CREATE EXPENSE
    # -----------------------------------

    def test_create_expense_success(self):
        payload = {
            "amount": "500.00",
            "category": "Food",
            "note": "Lunch",
            "date": "2026-09-22",
        }

        response = self.client.post(
            self.expenses_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            response.data["status"]
        )

        self.assertEqual(
            response.data["message"],
            "Expense created successfully."
        )

        self.assertEqual(
            Expense.objects.count(),
            1
        )

        expense = Expense.objects.first()

        self.assertEqual(
            expense.user,
            self.user
        )

        self.assertEqual(
            expense.amount,
            Decimal("500.00")
        )

    # -----------------------------------
    # INVALID AMOUNT
    # -----------------------------------

    def test_create_expense_with_invalid_amount(self):
        payload = {
            "amount": "0",
            "category": "Food",
            "note": "Lunch",
            "date": "2026-09-22",
        }

        response = self.client.post(
            self.expenses_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            response.data["status"]
        )

        self.assertIn(
            "amount",
            response.data["errors"]
        )

        self.assertEqual(
            Expense.objects.count(),
            0
        )

    # -----------------------------------
    # MISSING REQUIRED FIELD
    # -----------------------------------

    def test_create_expense_missing_category(self):
        payload = {
            "amount": "500.00",
            "note": "Lunch",
            "date": "2026-09-22",
        }

        response = self.client.post(
            self.expenses_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            response.data["status"]
        )

        self.assertIn(
            "category",
            response.data["errors"]
        )

    # -----------------------------------
    # UNAUTHENTICATED ACCESS
    # -----------------------------------

    def test_unauthenticated_user_cannot_create_expense(self):
        self.client.force_authenticate(user=None)

        payload = {
            "amount": "500.00",
            "category": "Food",
            "note": "Lunch",
            "date": "2026-09-22",
        }

        response = self.client.post(
            self.expenses_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # -----------------------------------
    # GET EXPENSES
    # -----------------------------------

    def test_get_expenses(self):
        Expense.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            category="Food",
            note="Lunch",
            date="2026-09-22",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Shopping",
            note="Clothes",
            date="2026-09-20",
        )

        response = self.client.get(
            self.expenses_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            response.data["status"]
        )

        self.assertEqual(
            len(response.data["data"]),
            2
        )

    # -----------------------------------
    # CATEGORY FILTER
    # -----------------------------------

    def test_filter_expenses_by_category(self):
        Expense.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            category="Food",
            note="Lunch",
            date="2026-09-22",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Shopping",
            note="Clothes",
            date="2026-09-20",
        )

        response = self.client.get(
            self.expenses_url,
            {
                "category": "Food"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.data["data"]

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["category"],
            "Food"
        )

    # -----------------------------------
    # DATE RANGE FILTER
    # -----------------------------------

    def test_filter_expenses_by_date_range(self):
        Expense.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            category="Food",
            note="Lunch",
            date="2026-09-22",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Shopping",
            note="Clothes",
            date="2026-09-10",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("300.00"),
            category="Travel",
            note="Trip",
            date="2026-08-20",
        )

        response = self.client.get(
            self.expenses_url,
            {
                "start_date": "2026-09-01",
                "end_date": "2026-09-30",
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.data["data"]

        self.assertEqual(
            len(data),
            2
        )

    # -----------------------------------
    # USER ISOLATION
    # -----------------------------------

    def test_user_can_only_see_own_expenses(self):
        Expense.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            category="Food",
            note="My expense",
            date="2026-09-22",
        )

        Expense.objects.create(
            user=self.other_user,
            amount=Decimal("9999.00"),
            category="Shopping",
            note="Other user's expense",
            date="2026-09-22",
        )

        response = self.client.get(
            self.expenses_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        data = response.data["data"]

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["amount"],
            "500.00"
        )

    # -----------------------------------
    # SUMMARY
    # -----------------------------------

    def test_summary_total_spend(self):
        Expense.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            category="Food",
            date="2026-09-10",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Shopping",
            date="2026-09-15",
        )

        response = self.client.get(
            self.summary_url,
            {
                "year": 2026,
                "month": 9,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        summary = response.data["data"]

        self.assertEqual(
            Decimal(str(summary["total_spend"])),
            Decimal("1500.00")
        )

    # -----------------------------------
    # SUMMARY BY CATEGORY
    # -----------------------------------

    def test_summary_spend_by_category(self):
        Expense.objects.create(
            user=self.user,
            amount=Decimal("500.00"),
            category="Food",
            date="2026-09-10",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("300.00"),
            category="Food",
            date="2026-09-15",
        )

        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Shopping",
            date="2026-09-20",
        )

        response = self.client.get(
            self.summary_url,
            {
                "year": 2026,
                "month": 9,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        categories = response.data["data"]["spend_by_category"]

        category_totals = {
            item["category"]: Decimal(str(item["total"])
            )
            for item in categories
        }

        self.assertEqual(
            category_totals["Food"],
            Decimal("800.00")
        )

        self.assertEqual(
            category_totals["Shopping"],
            Decimal("1000.00")
        )

    # -----------------------------------
    # MONTH OVER MONTH
    # -----------------------------------

    def test_month_over_month_change(self):
        # August
        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Food",
            date="2026-08-15",
        )

        # September
        Expense.objects.create(
            user=self.user,
            amount=Decimal("1500.00"),
            category="Food",
            date="2026-09-15",
        )

        response = self.client.get(
            self.summary_url,
            {
                "year": 2026,
                "month": 9,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        summary = response.data["data"]

        self.assertEqual(
            Decimal(str(summary["previous_month_total"])),
            Decimal("1000.00")
        )

        self.assertEqual(
            Decimal(str(summary["month_over_month_change"])),
            Decimal("50.0")
        )

    # -----------------------------------
    # CATEGORY >20% INSIGHT
    # -----------------------------------

    def test_category_insight_when_increase_is_more_than_20_percent(self):
        # August Food = 1000
        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Food",
            date="2026-08-15",
        )

        # September Food = 1500
        # Increase = 50%
        Expense.objects.create(
            user=self.user,
            amount=Decimal("1500.00"),
            category="Food",
            date="2026-09-15",
        )

        response = self.client.get(
            self.summary_url,
            {
                "year": 2026,
                "month": 9,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        insights = response.data["data"]["category_insights"]

        self.assertEqual(
            len(insights),
            1
        )

        insight = insights[0]

        self.assertEqual(
            insight["category"],
            "Food"
        )

        self.assertEqual(
            insight["percentage_increase"],
            50.0
        )

    # -----------------------------------
    # NO INSIGHT BELOW 20%
    # -----------------------------------

    def test_no_category_insight_when_increase_is_not_more_than_20_percent(self):
        # August Food = 1000
        Expense.objects.create(
            user=self.user,
            amount=Decimal("1000.00"),
            category="Food",
            date="2026-08-15",
        )

        # September Food = 1100
        # Increase = 10%
        Expense.objects.create(
            user=self.user,
            amount=Decimal("1100.00"),
            category="Food",
            date="2026-09-15",
        )

        response = self.client.get(
            self.summary_url,
            {
                "year": 2026,
                "month": 9,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        insights = response.data["data"]["category_insights"]

        self.assertEqual(
            len(insights),
            0
        )