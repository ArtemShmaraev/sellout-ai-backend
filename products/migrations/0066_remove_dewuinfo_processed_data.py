
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0065_alter_dewuinfo_formatted_manufacturer_sku_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dewuinfo',
            name='processed_data',
        ),
    ]
