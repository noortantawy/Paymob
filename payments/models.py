from django.db import models


class Merchant(models.Model):
    mid = models.AutoField(primary_key=True, verbose_name="MID")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Terminal(models.Model):
    tid = models.AutoField(primary_key=True, verbose_name="TID")
    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.CASCADE,
        related_name="terminals",
        db_column="mid",
    )
    serial_number = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.serial_number} ({self.merchant.name})"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="EGP")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.reference}"


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    terminal = models.ForeignKey(
        Terminal,
        on_delete=models.PROTECT,
        related_name="transactions",
        db_column="tid",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="EGP")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"], name="tx_status_idx"),
            models.Index(fields=["status", "created_at"], name="tx_status_created_idx"),
        ]

    def __str__(self):
        return f"Transaction #{self.pk} for {self.order.reference}"
