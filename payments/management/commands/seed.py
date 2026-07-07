"""Seed the database with merchants, terminals, orders, and transactions.

Usage:
    python manage.py seed                       # defaults: 1,000,000 transactions
    python manage.py seed --transactions 500000 --orders 50000
"""

import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction

from payments.models import Merchant, Order, Terminal, Transaction

ORDER_STATUSES = [c[0] for c in Order.Status.choices]
TX_STATUSES = [c[0] for c in Transaction.Status.choices]


class Command(BaseCommand):
    help = "Seed merchants, terminals, orders, and transactions for load testing."

    def add_arguments(self, parser):
        parser.add_argument("--merchants", type=int, default=50)
        parser.add_argument("--terminals-per-merchant", type=int, default=5)
        parser.add_argument("--orders", type=int, default=100_000)
        parser.add_argument("--transactions", type=int, default=1_000_000)
        parser.add_argument("--batch-size", type=int, default=5_000)
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing payment data before seeding.",
        )

    def handle(self, *args, **opts):
        if opts["flush"]:
            self.stdout.write("Flushing existing payment data...")
            Transaction.objects.all().delete()
            Order.objects.all().delete()
            Terminal.objects.all().delete()
            Merchant.objects.all().delete()

        batch = opts["batch_size"]

        # --- Merchants ---
        merchants = [
            Merchant(name=f"Merchant {i}", email=f"merchant{i}@seed.test")
            for i in range(opts["merchants"])
        ]
        Merchant.objects.bulk_create(merchants, batch_size=batch)
        mids = list(Merchant.objects.values_list("pk", flat=True))
        self.stdout.write(f"  merchants: {len(mids)}")

        # --- Terminals ---
        terminals = []
        seq = 0
        for mid in mids:
            for _ in range(opts["terminals_per_merchant"]):
                terminals.append(
                    Terminal(merchant_id=mid, serial_number=f"SN-{seq:07d}")
                )
                seq += 1
        Terminal.objects.bulk_create(terminals, batch_size=batch)
        tids = list(Terminal.objects.values_list("pk", flat=True))
        self.stdout.write(f"  terminals: {len(tids)}")

        # --- Orders ---
        self.stdout.write(f"Seeding {opts['orders']:,} orders...")
        self._bulk_stream(
            (
                Order(
                    reference=f"ORD-{i:09d}",
                    amount=Decimal(random.randrange(500, 500_000)) / 100,
                    status=random.choice(ORDER_STATUSES),
                )
                for i in range(opts["orders"])
            ),
            Order,
            batch,
            opts["orders"],
        )
        oids = list(Order.objects.values_list("pk", flat=True))

        # --- Transactions ---
        self.stdout.write(f"Seeding {opts['transactions']:,} transactions...")
        self._bulk_stream(
            (
                Transaction(
                    order_id=random.choice(oids),
                    terminal_id=random.choice(tids),
                    amount=Decimal(random.randrange(500, 500_000)) / 100,
                    status=random.choice(TX_STATUSES),
                )
                for _ in range(opts["transactions"])
            ),
            Transaction,
            batch,
            opts["transactions"],
        )
        self.stdout.write(self.style.SUCCESS("Done."))

    def _bulk_stream(self, gen, model, batch, total):
        """Consume a generator of unsaved instances, inserting in batches."""
        buf = []
        done = 0
        with db_transaction.atomic():
            for obj in gen:
                buf.append(obj)
                if len(buf) >= batch:
                    model.objects.bulk_create(buf, batch_size=batch)
                    done += len(buf)
                    buf.clear()
                    self.stdout.write(f"    {done:,}/{total:,}", ending="\r")
            if buf:
                model.objects.bulk_create(buf, batch_size=batch)
                done += len(buf)
        self.stdout.write(f"    {done:,}/{total:,} done")
