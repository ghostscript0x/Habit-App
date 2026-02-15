from datetime import datetime, timezone, timedelta
from app.models import HabitLog
from app.utils.cache import cache_get, cache_set


class StreakService:
    @staticmethod
    def calculate_current_streak(habit):
        cache_key = f"streak:current:{habit.id}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        logs = (
            HabitLog.query.filter_by(habit_id=habit.id)
            .order_by(HabitLog.completed_at.desc())
            .all()
        )

        logs = [log for log in logs if log.completed_at is not None]

        if not logs:
            result = 0
        elif habit.frequency == "daily":
            result = StreakService._calculate_daily_streak(logs)
        elif habit.frequency == "weekly":
            result = StreakService._calculate_weekly_streak(logs)
        elif habit.frequency == "monthly":
            result = StreakService._calculate_monthly_streak(logs)
        else:
            result = (
                logs[0].streak_count if logs and logs[0].streak_count is not None else 0
            )

        cache_set(cache_key, result, timeout=300)
        return result

    @staticmethod
    def _calculate_daily_streak(logs):
        if not logs:
            return 0

        streak = 0
        current_date = datetime.now(timezone.utc).date()

        for log in logs:
            if not log.completed_at:
                continue
            log_date = log.completed_at.date()

            if log_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif log_date == current_date + timedelta(days=1):
                current_date = log_date
                streak += 1
            else:
                break

        return streak

    @staticmethod
    def _calculate_weekly_streak(logs):
        if not logs:
            return 0

        streak = 0
        current_week = datetime.now(timezone.utc).isocalendar()[1]
        current_year = datetime.now(timezone.utc).year

        for log in logs:
            if not log.completed_at:
                continue
            log_week = log.completed_at.isocalendar()[1]
            log_year = log.completed_at.isocalendar()[0]

            if log_year == current_year and log_week == current_week:
                streak += 1
                current_week -= 1
                if current_week < 1:
                    current_year -= 1
                    current_week = 52
            else:
                break

        return streak

    @staticmethod
    def _calculate_monthly_streak(logs):
        if not logs:
            return 0

        streak = 0
        current_month = datetime.now(timezone.utc).month
        current_year = datetime.now(timezone.utc).year

        for log in logs:
            if not log.completed_at:
                continue
            log_month = log.completed_at.month
            log_year = log.completed_at.year

            if log_year == current_year and log_month == current_month:
                streak += 1
                current_month -= 1
                if current_month < 1:
                    current_year -= 1
                    current_month = 12
            else:
                break

        return streak

    @staticmethod
    def calculate_longest_streak(habit):
        cache_key = f"streak:longest:{habit.id}"
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

        logs = (
            HabitLog.query.filter_by(habit_id=habit.id)
            .order_by(HabitLog.completed_at.asc())
            .all()
        )

        if not logs:
            cache_set(cache_key, 0, timeout=300)
            return 0

        max_streak = 0
        current_streak = 0
        prev_date = None

        for log in logs:
            if not log.completed_at:
                continue
            log_date = log.completed_at.date()

            if prev_date is None:
                current_streak = 1
            elif log_date == prev_date:
                pass
            elif log_date == prev_date + timedelta(days=1):
                current_streak += 1
            else:
                current_streak = 1

            max_streak = max(max_streak, current_streak)
            prev_date = log_date

        cache_set(cache_key, max_streak, timeout=300)
        return max_streak

    @staticmethod
    def get_streak_info(habit):
        return {
            "current": StreakService.calculate_current_streak(habit),
            "longest": StreakService.calculate_longest_streak(habit),
        }
