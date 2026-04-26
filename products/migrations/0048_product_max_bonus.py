
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0047_alter_product_min_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='max_bonus',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
