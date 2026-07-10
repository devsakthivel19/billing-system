"""Initial billing schema."""

from __future__ import annotations

import apps.common.validators
import django.db.models.deletion
from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create invoice and denomination tables."""

    initial = True

    dependencies = [
        ("customers", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Denomination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.PositiveIntegerField(unique=True, validators=[MinValueValidator(1)])),
                ("available_quantity", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["-value"]},
        ),
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(db_index=True, max_length=32, unique=True)),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("tax_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("paid_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("balance_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="customers.customer")),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["invoice_number"], name="billing_inv_invoice_549473_idx"),
                    models.Index(fields=["created_at"], name="billing_inv_created_b8dc82_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="InvoiceItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(validators=[MinValueValidator(1)])),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("tax_percentage", models.DecimalField(decimal_places=2, max_digits=5, validators=[apps.common.validators.validate_percentage])),
                ("tax_amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="billing.invoice")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoice_items", to="products.product")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="BalanceDenomination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity_given", models.PositiveIntegerField(validators=[MinValueValidator(1)])),
                ("denomination", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="balance_returns", to="billing.denomination")),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="balance_denominations", to="billing.invoice")),
            ],
            options={
                "ordering": ["-denomination__value"],
                "constraints": [
                    models.UniqueConstraint(fields=("invoice", "denomination"), name="unique_invoice_balance_denomination"),
                ],
            },
        ),
    ]
