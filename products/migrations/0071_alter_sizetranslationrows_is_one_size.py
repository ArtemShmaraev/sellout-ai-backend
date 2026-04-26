
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0070_alter_gender_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sizetranslationrows',
            name='is_one_size',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
