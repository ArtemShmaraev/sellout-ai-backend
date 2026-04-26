
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_user_wait_list'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='patronymic',
            field=models.CharField(default='', max_length=100),
        ),
    ]
