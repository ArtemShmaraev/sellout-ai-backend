
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0032_alter_productunit_size_alter_productunit_size_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='productunit',
            name='bonus',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='productunit',
            name='total_profit',
            field=models.IntegerField(default=0),
        ),
    ]
