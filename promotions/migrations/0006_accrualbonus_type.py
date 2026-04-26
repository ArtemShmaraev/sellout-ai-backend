
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0005_promocode_ref_promo'),
    ]

    operations = [
        migrations.AddField(
            model_name='accrualbonus',
            name='type',
            field=models.CharField(default='Накопление', max_length=120),
        ),
    ]
