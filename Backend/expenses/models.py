from django.conf import settings
from django.db import models


class Expense(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    category = models.CharField(
        max_length=100,
    )

    note = models.TextField(
        blank=True,
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(
                fields=["user", "date"]
            ),
            models.Index(
                fields=["user", "category"]
            ),
        ]

    def __str__(self):
        return f"{self.category} - {self.amount}"