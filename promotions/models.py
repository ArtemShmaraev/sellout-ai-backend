import datetime

from django.db import models
from django.conf import settings
from datetime import date, timedelta, timezone
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone


class PromoCode(models.Model):
    string_representation = models.CharField(max_length=100, null=False, blank=False)
    discount_percentage = models.IntegerField(default=0)
    discount_absolute = models.IntegerField(default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              related_name="promo_codes")
    activation_count = models.IntegerField(default=0)
    max_activation_count = models.IntegerField(default=1)
    active_status = models.BooleanField(default=True)
    active_until_date = models.DateField(default=date.today)

    def check_promo(self, user_id=0):
        try:
            if self.activation_count >= self.max_activation_count:
                return 0, "Промокод закончился"
            if self.active_status and self.active_until_date >= datetime.date.today():
                return 1, "Промокод применен"
            else:
                return 0, "Промокод не активен"
        except:
            return 0, "Промокод не найден"

    def __str__(self):
        return self.string_representation


class AccrualBonus(models.Model):
    amount = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)

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
