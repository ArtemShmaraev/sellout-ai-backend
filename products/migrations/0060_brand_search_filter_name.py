
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0059_alter_gender_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='search_filter_name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
