
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0011_rename_products_configurationunit_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverytype',
            name='days',
            field=models.IntegerField(default=0),
        ),
    ]
