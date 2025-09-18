import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from bot.user_data import get_all_user_ids, get_user_data
from apis.google_calendar import get_first_event_for_day
from apis.cp_sk_scraper import find_latest_departure

# This is a placeholder for the morning job, which we'll define in the next step.
async def morning_notifier_job(bot: Bot, user_id: int, message: str):
    """A simple job that sends a pre-defined message to a user."""
    await bot.send_message(user_id, message)

async def evening_planning_job(bot: Bot, scheduler):
    """
    Runs every evening to plan the next day for all users.
    """
    print("Running evening planning job...")
    user_ids = get_all_user_ids()

    for user_id in user_ids:
        # Check if the user has configured the necessary data
        home_loc = get_user_data(user_id, 'home_location')
        uni_loc = get_user_data(user_id, 'university_location')
        has_google_token = get_user_data(user_id, 'google_refresh_token')

        if not (home_loc and uni_loc and has_google_token):
            # Skip users who haven't completed setup
            continue

        try:
            # 1. Get the first event for the next day
            tomorrow = datetime.now().date() + timedelta(days=1)
            event = await get_first_event_for_day(user_id, tomorrow)

            if not event:
                await bot.send_message(user_id, "На завтра у вас нет запланированных пар. Отдыхайте!")
                continue

            event_summary = event['summary']
            event_start_str = event['start']
            # Parse the event start time
            event_start_time = datetime.fromisoformat(event_start_str)

            # 2. Calculate the commute
            origin_stop = home_loc.get('stop')
            dest_stop = uni_loc.get('stop')

            if not (origin_stop and dest_stop):
                await bot.send_message(user_id, "Не могу рассчитать маршрут: не заданы названия остановок.")
                continue

            departure_time_str = await find_latest_departure(origin_stop, dest_stop, event_start_time)

            if not departure_time_str:
                await bot.send_message(user_id, f"Не удалось рассчитать время в пути для завтрашней пары '{event_summary}'.")
                continue

            # 3. Send the evening summary
            departure_dt = datetime.strptime(departure_time_str, "%H:%M").time()
            summary_message = (
                f"Добрый вечер! Ваш план на завтра:\n"
                f"- Первая пара: '{event_summary}' в {event_start_time.strftime('%H:%M')}.\n"
                f"- Чтобы успеть, вам нужно выехать не позднее {departure_time_str}.\n"
                f"Хорошего вечера!"
            )
            await bot.send_message(user_id, summary_message)

            # 4. Schedule the dynamic morning job
            # Departure time is today's date + departure time, then add a day for tomorrow
            departure_datetime = datetime.combine(datetime.now().date(), departure_dt) + timedelta(days=1)
            morning_alert_time = departure_datetime - timedelta(hours=1)

            morning_message = f"Доброе утро! Напоминаю, ваша первая пара сегодня в {event_start_time.strftime('%H:%M')}. Не забудьте выехать в {departure_time_str}!"

            scheduler.add_job(
                morning_notifier_job,
                'date',
                run_date=morning_alert_time,
                kwargs={'bot': bot, 'user_id': user_id, 'message': morning_message}
            )
            print(f"Scheduled morning job for user {user_id} at {morning_alert_time}")

        except Exception as e:
            print(f"Failed to process evening plan for user {user_id}: {e}")
            # Optionally, send an error message to the user
            await bot.send_message(user_id, "Произошла ошибка при планировании вашего завтрашнего дня.")
