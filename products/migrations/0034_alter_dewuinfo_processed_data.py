
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0033_product_size_table_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dewuinfo',
            name='processed_data',
            field=models.JSONField(default=list),
        ),
    ]
