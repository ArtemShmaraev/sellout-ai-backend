
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_clothes_size_user_height_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='preferred_clothes_size_table',
            new_name='preferred_clothes_size_row',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='preferred_shoes_size_table',
            new_name='preferred_shoes_size_row',
        ),
    ]
