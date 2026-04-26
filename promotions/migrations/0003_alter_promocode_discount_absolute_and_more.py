
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='discount_absolute',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='discount_percentage',
            field=models.IntegerField(default=0),
        ),
    ]
