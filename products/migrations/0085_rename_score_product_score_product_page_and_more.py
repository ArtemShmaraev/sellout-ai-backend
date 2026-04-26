
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0084_product_score'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='score',
            new_name='score_product_page',
        ),
        migrations.AddField(
            model_name='category',
            name='score_product_page',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='collab',
            name='score_product_page',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='line',
            name='score_product_page',
            field=models.IntegerField(default=0),
        ),
    ]
