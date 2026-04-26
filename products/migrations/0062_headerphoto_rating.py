
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0061_remove_brand_search_filter_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='headerphoto',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]
