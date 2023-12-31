# Generated by Django 4.2.3 on 2023-07-16 02:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_embed", "0003_job_user_task_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Environment",
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
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Host",
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
                ("name", models.CharField(max_length=255)),
                ("ip_address", models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name="JobType",
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
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name="job",
            name="output",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="Tool",
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
                ("name", models.CharField(max_length=255)),
                ("environments", models.ManyToManyField(to="django_embed.environment")),
                (
                    "job_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_embed.jobtype",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="environment",
            name="host",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="django_embed.host"
            ),
        ),
        migrations.CreateModel(
            name="Config",
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
                ("name", models.CharField(max_length=255)),
                ("config_data", models.TextField()),
                (
                    "tool",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="django_embed.tool",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="job",
            name="host",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_embed.host",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="tool",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_embed.tool",
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="job_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_embed.jobtype",
            ),
        ),
    ]
