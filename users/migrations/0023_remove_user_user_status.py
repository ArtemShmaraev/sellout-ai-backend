
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_user_user_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_status',
        ),
    ]
