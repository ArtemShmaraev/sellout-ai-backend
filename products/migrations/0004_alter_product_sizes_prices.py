
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_sizes_prices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sizes_prices',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
