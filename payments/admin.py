from django.contrib import admin

from .models import Merchant, Order, Terminal, Transaction


class TerminalInline(admin.TabularInline):
    model = Terminal
    extra = 0


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("mid", "name", "email", "is_active", "created_at")
    search_fields = ("name", "email")
    inlines = [TerminalInline]


@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = ("tid", "serial_number", "label", "merchant", "is_active")
    search_fields = ("serial_number", "label", "merchant__name")
    list_filter = ("is_active",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "amount", "currency", "status", "created_at")
    search_fields = ("reference",)
    list_filter = ("status",)
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "terminal", "amount", "currency", "status", "created_at")
    search_fields = ("order__reference", "terminal__serial_number")
    list_filter = ("status",)
