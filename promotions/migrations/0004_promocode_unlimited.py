
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0003_alter_promocode_discount_absolute_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='unlimited',
            field=models.BooleanField(default=False),
        ),
    ]
