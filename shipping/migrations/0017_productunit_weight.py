
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0016_productunit_size_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='weight',
            field=models.IntegerField(default=1),
        ),
    ]
