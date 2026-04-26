
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0044_deliverytype_commission'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverytype',
            name='currency',
            field=models.FloatField(default=12.9),
        ),
    ]
