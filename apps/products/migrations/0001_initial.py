"""Initial product schema."""

from __future__ import annotations

import apps.common.validators
from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the product table."""

    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_id", models.CharField(db_index=True, max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("available_stock", models.PositiveIntegerField(default=0)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])),
                ("tax_percentage", models.DecimalField(decimal_places=2, max_digits=5, validators=[apps.common.validators.validate_percentage])),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["product_id"], name="products_pr_product_3fdb84_idx"),
                    models.Index(fields=["is_active", "name"], name="products_pr_is_acti_3ba8d5_idx"),
                ],
            },
        ),
    ]
