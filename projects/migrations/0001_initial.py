# Generated migration for projects app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Název projektu', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Podrobný popis projektu')),
                ('status', models.CharField(choices=[('draft', 'Návrh'), ('active', 'Aktivní'), ('completed', 'Hotovo'), ('archived', 'Archivováno'), ('cancelled', 'Zrušeno')], default='draft', help_text='Status projektu', max_length=20)),
                ('budget', models.DecimalField(decimal_places=2, default=0, help_text='Celkový rozpočet projektu', max_digits=10)),
                ('estimated_hours', models.DecimalField(decimal_places=2, default=0, help_text='Odhadnuté hodiny', max_digits=8)),
                ('start_date', models.DateField(blank=True, help_text='Datum začátku projektu', null=True)),
                ('end_date', models.DateField(blank=True, help_text='Deadline projektu', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(help_text='Klient, pro kterého je projekt', on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='clients.client')),
                ('user', models.ForeignKey(help_text='Freelancer, který má projekt', on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projects_project',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['user', '-created_at'], name='projects_pr_user_id_3f5a2b_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['user', 'status'], name='projects_pr_user_id_7d2c1a_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['client', '-created_at'], name='projects_pr_client__8a4f3c_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['user', 'status', '-end_date'], name='projects_pr_user_id_5c7e2d_idx'),
        ),
    ]
