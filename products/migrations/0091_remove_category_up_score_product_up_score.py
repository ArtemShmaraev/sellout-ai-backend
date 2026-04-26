
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0090_category_up_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='up_score',
        ),
        migrations.AddField(
            model_name='product',
            name='up_score',
            field=models.BooleanField(default=False),
        ),
    ]
