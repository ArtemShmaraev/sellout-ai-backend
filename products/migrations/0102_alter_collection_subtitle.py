
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0101_collection_subtitle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='subtitle',
            field=models.CharField(default='', max_length=1024),
        ),
    ]
