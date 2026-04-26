
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_user_patronymic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='happy_birthday',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
