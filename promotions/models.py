import datetime

from django.db import models
from django.conf import settings
from datetime import date, timedelta, timezone
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

# from orders.models import Order


class PromoCode(models.Model):
    string_representation = models.CharField(max_length=100, null=False, blank=False)
    discount_percentage = models.IntegerField(default=0)
    discount_absolute = models.IntegerField(default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              related_name="promo_codes")
    activation_count = models.IntegerField(default=0)
    max_activation_count = models.IntegerField(default=1)
    active_status = models.BooleanField(default=True)
    unlimited = models.BooleanField(default=False)
    ref_promo = models.BooleanField(default=False)
    active_until_date = models.DateField(default=date.today)


    def check_promo_in_cart(self, cart):
        promo_sale = 0
        if cart.user.user_status.base:
            flag_order = cart.user.orders.exists()

            if self.ref_promo and not flag_order:
                ref_sale = 0
                if 3000 <= cart.final_amount < 5000:
                    ref_sale = 500
                elif 5000 <= cart.final_amount < 15000:
                    ref_sale = 750
                elif 15000 <= cart.final_amount < 35000:
                    ref_sale = 1000
                elif 35000 <= cart.final_amount < 70000:
                    ref_sale = 1250
                elif 70000 <= cart.final_amount < 130000:
                    ref_sale = 2000
                elif 130000 <= cart.final_amount < 150000:
                    ref_sale = 2500
                elif cart.final_amount >= 150000:
                    ref_sale = 3000
                promo_sale = ref_sale

            elif self.discount_percentage > 0:
                pred = round(cart.final_amount * (100 - self.discount_percentage) // 100)
                promo_sale = cart.final_amount - pred

            elif self.discount_absolute > 0:
                pred = round(cart.final_amount - self.discount_absolute)
                promo_sale = cart.final_amount - pred

        return promo_sale

    def check_promo(self, cart):
        promo_sale = 0
        if cart.user.user_status.base:
            flag_order = cart.user.orders.exists()

            if self.ref_promo and not flag_order:
                ref_sale = 0
                if 3000 <= cart.final_amount < 5000:
                    ref_sale = 500
                elif 5000 <= cart.final_amount < 15000:
                    ref_sale = 750
                elif 15000 <= cart.final_amount < 35000:
                    ref_sale = 1000
                elif 35000 <= cart.final_amount < 70000:
                    ref_sale = 1250
                elif 70000 <= cart.final_amount < 130000:
                    ref_sale = 2000
                elif 130000 <= cart.final_amount < 150000:
                    ref_sale = 2500
                elif cart.final_amount >= 150000:
                    ref_sale = 3000
                promo_sale = ref_sale

            elif self.discount_percentage > 0:
                pred = round(cart.final_amount * (100 - self.discount_percentage) // 100)
                promo_sale = cart.final_amount - pred

            elif self.discount_absolute > 0:
                pred = round(cart.final_amount - self.discount_absolute)
                promo_sale = cart.final_amount - pred

            if (self.activation_count >= self.max_activation_count) and not self.unlimited:
                return 0, "Промокод закончился"
            if ((
                        self.active_status and self.active_until_date >= datetime.date.today()) or self.unlimited) and promo_sale > 0:
                return 1, f"Скидка по промокоду  {promo_sale}P", promo_sale
            else:
                return 0, "Промокод не активен"
        return 1, "Для Вас уже учтены все скидки", promo_sale


    def check_anon_promo(self, final_amount, total_amount):
        promo_sale = 0
        if self.ref_promo:
            ref_sale = 0
            if 3000 <= final_amount < 5000:
                ref_sale = 500
            elif 5000 <= final_amount < 15000:
                ref_sale = 750
            elif 15000 <= final_amount < 35000:
                ref_sale = 1000
            elif 35000 <= final_amount < 70000:
                ref_sale = 1250
            elif 70000 <= final_amount < 130000:
                ref_sale = 2000
            elif 130000 <= final_amount < 150000:
                ref_sale = 2500
            elif final_amount >= 150000:
                ref_sale = 3000
            promo_sale = ref_sale

        elif self.discount_percentage > 0:
            pred = round(final_amount * (100 - self.discount_percentage) // 100)
            promo_sale = final_amount - pred
        elif self.discount_absolute > 0:
            pred = round(final_amount - self.discount_absolute)
            promo_sale = final_amount - pred

        if (self.activation_count >= self.max_activation_count) and not self.unlimited:
            return 0, "Промокод закончился"
        if ((
                    self.active_status and self.active_until_date >= datetime.date.today()) or self.unlimited) and promo_sale > 0:
            return 1, f"Скидка по промокоду  {promo_sale}P", promo_sale
        else:
            return 0, "Промокод не активен"






    def __str__(self):
        return self.string_representation


class AccrualBonus(models.Model):
    amount = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)
    type = models.CharField(default="Накопление", max_length=120)

    def is_expired(self):
        return self.date + timedelta(days=365) < datetime.datetime.now()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Trigger the signal to update the related Bonuses model
        update_bonus_amount(sender=self.__class__, instance=self)


class Bonuses(models.Model):
    accrual = models.ManyToManyField("promotions.AccrualBonus", blank=True, related_name="bonuses") # начисление бонуслв (количество, дата)
    total_amount = models.IntegerField(default=0)

    def deduct_bonus(self, amount):
        sorted_accrual = self.accrual.order_by('-date')
        for accrual_bonus in sorted_accrual:
            if accrual_bonus.amount > amount:
                accrual_bonus.amount -= amount
                accrual_bonus.save()
                break
            else:
                amount -= accrual_bonus.amount
                accrual_bonus.amount = 0
                accrual_bonus.save()
                accrual_bonus.delete()
        self.update_total_amount()

    def update_total_amount(self):
        self.total_amount = self.accrual.aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.save()

    def __str__(self):
        user = self.user.all().first()  # Получить первого пользователя, связанного с этим объектом Bonuses
        return user.username if user is not None else ''


@receiver(m2m_changed, sender=Bonuses.accrual.through)
def update_total_amount(sender, instance, action, **kwargs):
    if action:
        instance.update_total_amount()


@receiver(post_delete, sender=AccrualBonus)
def update_total_amount_after_delete(sender, instance, **kwargs):
    bonuses = Bonuses.objects.filter(accrual=instance)
    for bonus in bonuses:
        bonus.update_total_amount()


@receiver(post_save, sender=AccrualBonus)
def update_bonus_amount(sender, instance, **kwargs):
    if instance.bonuses.all():
        bonus = instance.bonuses.first()
        bonus.update_total_amount()
        bonus.save()
