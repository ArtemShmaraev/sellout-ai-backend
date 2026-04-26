
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0052_orderunit_on_way_to_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cancel_reason',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.CharField(blank=True, default='', max_length=4048),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='track_numbers',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
