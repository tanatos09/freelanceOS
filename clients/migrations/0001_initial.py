# Generated migration for clients app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Název firmy nebo jméno osoby', max_length=255)),
                ('email', models.EmailField(help_text='Kontaktní email', max_length=254)),
                ('phone', models.CharField(blank=True, help_text='Telefonní číslo', max_length=20)),
                ('company', models.CharField(blank=True, help_text='Název společnosti (pokud se liší od name)', max_length=255)),
                ('notes', models.TextField(blank=True, help_text='Interní poznámky (není vidět klientovi)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='Freelancer, kterému patří tento klient', on_delete=django.db.models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'clients_client',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['user', '-created_at'], name='clients_cl_user_id_24a1f5_idx'),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['user', 'name'], name='clients_cl_user_id_7d2a3b_idx'),
        ),
        migrations.AddConstraint(
            model_name='client',
            constraint=models.UniqueConstraint(fields=['user', 'email'], name='unique_user_client_email'),
        ),
    ]
