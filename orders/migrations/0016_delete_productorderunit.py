
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0015_alter_order_status_alter_orderunit_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductOrderUnit',
        ),
    ]
