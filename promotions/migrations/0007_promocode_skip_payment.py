
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0006_accrualbonus_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='skip_payment',
            field=models.BooleanField(default=False),
        ),
    ]
