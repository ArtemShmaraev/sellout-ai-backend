
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0098_collab_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='percentage_sale',
        ),
    ]
