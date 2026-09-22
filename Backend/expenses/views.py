import logging
from datetime import date

from django.db import DatabaseError

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense
from .serializers import ExpenseSerializer
from .services import get_month_summary


logger = logging.getLogger(__name__)


class ExpenseListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            queryset = Expense.objects.filter(
                user=request.user
            )

            category = request.query_params.get(
                "category"
            )

            start_date = request.query_params.get(
                "start_date"
            )

            end_date = request.query_params.get(
                "end_date"
            )

            if category:
                queryset = queryset.filter(
                    category__iexact=category.strip()
                )

            if start_date:

                try:
                    parsed_start_date = date.fromisoformat(
                        start_date
                    )

                except ValueError:

                    return Response(
                        {
                            "status": False,
                            "status_code": 400,
                            "message": (
                                "Invalid start_date. "
                                "Use YYYY-MM-DD."
                            ),
                            "data": None,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                queryset = queryset.filter(
                    date__gte=parsed_start_date
                )

            if end_date:

                try:
                    parsed_end_date = date.fromisoformat(
                        end_date
                    )

                except ValueError:

                    return Response(
                        {
                            "status": False,
                            "status_code": 400,
                            "message": (
                                "Invalid end_date. "
                                "Use YYYY-MM-DD."
                            ),
                            "data": None,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                queryset = queryset.filter(
                    date__lte=parsed_end_date
                )

            if (
                start_date
                and end_date
                and parsed_start_date > parsed_end_date
            ):

                return Response(
                    {
                        "status": False,
                        "status_code": 400,
                        "message": (
                            "start_date cannot be "
                            "after end_date."
                        ),
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ExpenseSerializer(
                queryset,
                many=True,
            )

            return Response(
                {
                    "status": True,
                    "status_code": 200,
                    "message": "Expenses fetched successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except DatabaseError:

            logger.exception(
                "Database error while fetching expenses"
            )

            return Response(
                {
                    "status": False,
                    "status_code": 500,
                    "message": (
                        "Unable to fetch expenses."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception:

            logger.exception(
                "Unexpected error while fetching expenses"
            )

            return Response(
                {
                    "status": False,
                    "status_code": 500,
                    "message": (
                        "Something went wrong. "
                        "Please try again later."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):

        try:
            serializer = ExpenseSerializer(
                data=request.data
            )

            if not serializer.is_valid():

                return Response(
                    {
                        "status": False,
                        "status_code": 400,
                        "message": "Expense creation failed.",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            expense = serializer.save(
                user=request.user
            )

            return Response(
                {
                    "status": True,
                    "status_code": 201,
                    "message": "Expense created successfully.",
                    "data": ExpenseSerializer(
                        expense
                    ).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except DatabaseError:

            logger.exception(
                "Database error while creating expense"
            )

            return Response(
                {
                    "status": False,
                    "status_code": 500,
                    "message": (
                        "Unable to save expense."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception:

            logger.exception(
                "Unexpected error while creating expense"
            )

            return Response(
                {
                    "status": False,
                    "status_code": 500,
                    "message": (
                        "Something went wrong. "
                        "Please try again later."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SummaryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            today = date.today()

            year = request.query_params.get(
                "year",
                today.year,
            )

            month = request.query_params.get(
                "month",
                today.month,
            )

            try:
                year = int(year)
                month = int(month)

            except ValueError:

                return Response(
                    {
                        "status": False,
                        "status_code": 400,
                        "message": (
                            "year and month must be integers."
                        ),
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if month < 1 or month > 12:

                return Response(
                    {
                        "status": False,
                        "status_code": 400,
                        "message": (
                            "month must be between 1 and 12."
                        ),
                        "data": None,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            summary = get_month_summary(
                user=request.user,
                year=year,
                month=month,
            )

            return Response(
                {
                    "status": True,
                    "status_code": 200,
                    "message": "Summary fetched successfully.",
                    "data": summary,
                },
                status=status.HTTP_200_OK,
            )

        except DatabaseError:

            logger.exception(
                "Database error while generating summary"
            )

            return Response(
                {
                    "status": False,
                    "status_code": 500,
                    "message": (
                        "Unable to generate summary."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception:

            logger.exception(
                "Unexpected error while generating summary"
            )

            return Response(
                {
                    "status": False,
                    "status_code": 500,
                    "message": (
                        "Something went wrong. "
                        "Please try again later."
                    ),
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )