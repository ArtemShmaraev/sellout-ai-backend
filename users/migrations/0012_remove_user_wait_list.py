
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_user_wait_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='wait_list',
        ),
    ]
