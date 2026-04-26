
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_partner_spamemail'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='extra_contact',
            field=models.CharField(default='', max_length=64),
        ),
    ]
