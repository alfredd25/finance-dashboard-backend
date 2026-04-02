from rest_framework import serializers
from apps.finance.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id", "amount", "type", "category", "date", "notes",
            "created_by", "created_by_email", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_email", "created_at", "updated_at"]

    def validate_type(self, value):
        valid = [t[0] for t in Transaction.Type.choices]
        if value not in valid:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(valid)}.")
        return value

    def validate_category(self, value):
        valid = [c[0] for c in Transaction.Category.choices]
        if value not in valid:
            raise serializers.ValidationError(f"Category must be one of: {', '.join(valid)}.")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class TransactionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["amount", "type", "category", "date", "notes"]

    def validate_type(self, value):
        valid = [t[0] for t in Transaction.Type.choices]
        if value not in valid:
            raise serializers.ValidationError(f"Type must be one of: {', '.join(valid)}.")
        return value

    def validate_category(self, value):
        valid = [c[0] for c in Transaction.Category.choices]
        if value not in valid:
            raise serializers.ValidationError(f"Category must be one of: {', '.join(valid)}.")
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value