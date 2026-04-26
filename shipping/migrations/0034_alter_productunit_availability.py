
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0033_productunit_bonus_productunit_total_profit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productunit',
            name='availability',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]
