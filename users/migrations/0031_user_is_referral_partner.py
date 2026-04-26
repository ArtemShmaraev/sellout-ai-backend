
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_alter_user_verify_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_referral_partner',
            field=models.BooleanField(default=False),
        ),
    ]
