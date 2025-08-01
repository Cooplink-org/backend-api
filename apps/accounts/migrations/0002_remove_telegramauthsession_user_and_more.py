# Generated by Django 5.2.3 on 2025-07-06 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='telegramauthsession',
            name='user',
        ),
        migrations.RemoveIndex(
            model_name='user',
            name='accounts_us_telegra_de466c_idx',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='telegram_id',
            new_name='github_id',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='telegram_username',
            new_name='github_username',
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['github_id'], name='accounts_us_github__55cc0c_idx'),
        ),
        migrations.DeleteModel(
            name='TelegramAuthSession',
        ),
    ]
