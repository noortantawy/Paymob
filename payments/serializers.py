from decimal import Decimal

from rest_framework import serializers

from .models import Order, Terminal


class PaymentSerializer(serializers.Serializer):
    order_reference = serializers.CharField(max_length=100)
    tid = serializers.IntegerField()
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    currency = serializers.CharField(max_length=3, default="EGP")

    def validate_order_reference(self, value):
        try:
            order = Order.objects.get(reference=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        if order.status == Order.Status.PAID:
            raise serializers.ValidationError("Order is already paid.")
        if order.status == Order.Status.CANCELLED:
            raise serializers.ValidationError("Order is cancelled.")
        self.context["order"] = order
        return value

    def validate_tid(self, value):
        try:
            terminal = Terminal.objects.get(pk=value)
        except Terminal.DoesNotExist:
            raise serializers.ValidationError("Terminal not found.")
        if not terminal.is_active:
            raise serializers.ValidationError("Terminal is inactive.")
        self.context["terminal"] = terminal
        return value
