# Generated by Django 5.1.11 on 2025-06-16 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("texts", "0003_triggerentity"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attribute",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                ("key", models.CharField(max_length=256, verbose_name="Key")),
                (
                    "value",
                    models.CharField(
                        blank=True, max_length=512, null=True, verbose_name="Value"
                    ),
                ),
            ],
            options={
                "verbose_name": "Attribute",
                "verbose_name_plural": "Attributes",
                "ordering": ("key", "value"),
                "unique_together": {("key", "value")},
            },
        ),
    ]
