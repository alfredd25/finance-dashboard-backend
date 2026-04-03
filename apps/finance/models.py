import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.users.models import User


class ActiveTransactionManager(models.Manager):
    """Default manager — excludes soft-deleted records."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class AllTransactionManager(models.Manager):
    """Unfiltered manager — includes soft-deleted records. Admin use only."""
    def get_queryset(self):
        return super().get_queryset()


class Transaction(models.Model):

    class Type(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    class Category(models.TextChoices):
        SALARY = "salary", "Salary"
        FREELANCE = "freelance", "Freelance"
        INVESTMENT = "investment", "Investment"
        RENT = "rent", "Rent"
        UTILITIES = "utilities", "Utilities"
        GROCERIES = "groceries", "Groceries"
        TRANSPORT = "transport", "Transport"
        HEALTHCARE = "healthcare", "Healthcare"
        ENTERTAINMENT = "entertainment", "Entertainment"
        TRAVEL = "travel", "Travel"
        EDUCATION = "education", "Education"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveTransactionManager()
    all_objects = AllTransactionManager()

    class Meta:
        db_table = "transactions"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.type} | {self.category} | {self.amount} on {self.date}"

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])