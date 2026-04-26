
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0027_remove_productunit_extra_delivery_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='approximate_price_with_delivery_in_rub',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
