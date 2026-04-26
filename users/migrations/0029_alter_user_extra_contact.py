
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0028_user_extra_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='extra_contact',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
    ]
