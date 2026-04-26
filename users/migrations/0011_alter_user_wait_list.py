
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0010_configurationunit'),
        ('users', '0010_user_wait_list'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='wait_list',
            field=models.ManyToManyField(blank=True, related_name='wait_list_users', to='shipping.configurationunit'),
        ),
    ]
