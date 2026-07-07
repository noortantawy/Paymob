from django.test import TestCase

# Create your tests here.
# 2. Create a login user + known test data (Paymob shell), so you have a valid tid and order_reference:
# cd Paymob && python manage.py shell
# from django.contrib.auth.models import User
# from payments.models import Merchant, Terminal, Order
# from decimal import Decimal

# User.objects.create_superuser("admin", "admin@test.com", "admin123")

# m = Merchant.objects.create(name="Test Merchant", email="m@test.com")
# t = Terminal.objects.create(merchant=m, serial_number="SN-TEST-1")
# Order.objects.create(reference="ORD-TEST-1", amount=Decimal("100.00"))

# print("TID:", t.tid, "| ORDER:", "ORD-TEST-1")
# exit()

# ---
# Postman requests

# Base URL: http://localhost:8001

# 1. Get JWT token — POST /auth/token

# - Body → raw / JSON:
# { "username": "admin", "password": "admin123" }
# - Response gives { "access": "...", "refresh": "..." }. Copy access.
# - Tip: in the request's Tests tab, auto-save the token:
# pm.environment.set("token", pm.response.json().access);

# 2. Pay — POST /pay

# - Authorization tab → Type Bearer Token → {{token}} (or paste the access token).
# - Body → raw / JSON:
# {
#   "order_reference": "ORD-TEST-1",
#   "tid": 1,
#   "amount": "100.00",
#   "currency": "EGP"
# }

# ▎ Use the tid printed in setup. Since the Bank returns yes/no/timeout at random, send this a few times to see all outcomes:

# ┌────────────┬──────┬──────────────────────────────────────┐
# │ Bank rolls │ HTTP │ Response transaction_status / reason │
# ├────────────┼──────┼──────────────────────────────────────┤
# │ accepted   │ 201  │ success / null                       │
# ├────────────┼──────┼──────────────────────────────────────┤
# │ rejected   │ 402  │ failed / rejected                    │
# ├────────────┼──────┼──────────────────────────────────────┤
# │ timeout    │ 504  │ pending / bank_timeout               │
# └────────────┴──────┴──────────────────────────────────────┘

# 3. Refresh token — POST /auth/token/refresh

# { "refresh": "<refresh-token-from-step-1>" }

# ---