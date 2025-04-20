import threading

import schedule
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum

from promotions.models import Bonuses, AccrualBonus

def deduct_expired_bonuses():
    # Получаем текущую дату и время
    now = datetime.now()

    # Вычисляем дату, на которую считаются бонусы устаревшими (за 30 дней)
    expiration_date = now - timedelta(days=30)

    # Получаем все экземпляры модели Bonuses
    bonuses = Bonuses.objects.all()

    for bonus in bonuses:
        accrual_bonuses = bonus.accrual.all()

        # Фильтруем устаревшие бонусы по дате
        expired_bonuses = accrual_bonuses.filter(date__lte=expiration_date)

        if expired_bonuses:
            # Списываем истекшие бонусы из общей суммы
            total_deduction = expired_bonuses.aggregate(deduction=Sum('amount'))['deduction'] or 0
            bonus.total_amount -= total_deduction

            # Удаляем истекшие бонусы из связи
            expired_bonuses.delete()

            # Сохраняем обновленный экземпляр модели Bonuses
            bonus.save()

    print("Бонусы успешно списаны.")

# Запускаем функцию списывания устаревших бонусов раз в день в 00:00
# schedule.every().day.at("15:27").do(deduct_expired_bonuses)

def run_scheduler():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            deduct_expired_bonuses()
        time.sleep(60)  # Проверка каждую минуту

scheduler_thread = threading.Thread(target=run_scheduler)
# scheduler_thread.start()


# def run_bonus_scheduler():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
#
#
# if settings.RUN_BONUS_SCHEDULER:
#     print(10)
#     run_bonus_scheduler()
