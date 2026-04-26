
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_alter_product_colors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='dewu_info',
        ),
    ]
