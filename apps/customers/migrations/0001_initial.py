"""Initial customer schema."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the customer table."""

    initial = True

    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(db_index=True, max_length=254, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["email"],
                "indexes": [models.Index(fields=["email"], name="customers_c_email_f3b102_idx")],
            },
        ),
    ]
