from decimal import Decimal

from rest_framework import serializers

from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense

        fields = [
            "id",
            "amount",
            "category",
            "note",
            "date",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_amount(self, value):

        if value <= Decimal("0"):
            raise serializers.ValidationError(
                "Amount must be greater than 0."
            )

        return value

    def validate_category(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Category cannot be empty."
            )

        return value

    def validate_note(self, value):

        return value.strip()