
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0083_alter_sizetable_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
