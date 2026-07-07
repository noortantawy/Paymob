import uuid
from decimal import Decimal

from django.db import transaction as db_transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, Transaction
from .serializers import PaymentSerializer
from .services import authorize_payment


class PayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = serializer.context["order"]
        terminal = serializer.context["terminal"]
        amount = serializer.validated_data["amount"]
        currency = serializer.validated_data["currency"]

        tx = Transaction.objects.create(
            order=order,
            terminal=terminal,
            amount=amount,
            currency=currency,
            status=Transaction.Status.PENDING,
        )

        bank_response = authorize_payment(
            mid=terminal.merchant_id,
            tid=terminal.tid,
            amount=amount,
            currency=currency,
            order_reference=order.reference,
        )
        outcome = bank_response["outcome"]

        with db_transaction.atomic():
            if outcome == "approved":
                tx.status = Transaction.Status.SUCCESS
                order.status = Order.Status.PAID
                order.save(update_fields=["status", "updated_at"])
                tx.save(update_fields=["status", "updated_at"])
            elif outcome == "declined":
                tx.status = Transaction.Status.FAILED
                tx.save(update_fields=["status", "updated_at"])
            # "timeout": outcome unknown, leave the transaction PENDING for
            # reconciliation rather than falsely marking it failed.

        body = {
            "transaction_id": tx.pk,
            "order_reference": order.reference,
            "order_status": order.status,
            "transaction_status": tx.status
        }
        if outcome == "approved":
            return Response(body, status=status.HTTP_201_CREATED)
        if outcome == "timeout":
            return Response(body, status=status.HTTP_504_GATEWAY_TIMEOUT)
        return Response(body, status=status.HTTP_402_PAYMENT_REQUIRED)
