
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0023_deliverytype_days_max_to_international_warehouse_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='absolute_profit',
            field=models.IntegerField(default=0),
        ),
    ]
