
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_user_is_referral_partner'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referral_data',
            field=models.JSONField(default={'client_bonus_amounts': None, 'client_sale_amounts': None, 'order_amounts': ['От 3000₽', 'От 35000₽'], 'partner_bonus_amounts': ['500₽', '1000₽'], 'promo_text': None}),
        ),
    ]
