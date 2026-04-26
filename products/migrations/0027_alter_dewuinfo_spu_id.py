
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_sginfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dewuinfo',
            name='spu_id',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
