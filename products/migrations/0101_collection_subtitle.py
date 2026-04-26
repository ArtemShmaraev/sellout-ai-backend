
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0100_remove_collection_is_collab_product_collections'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='subtitle',
            field=models.CharField(default='', max_length=255),
        ),
    ]
