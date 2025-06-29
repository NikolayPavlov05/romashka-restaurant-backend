from datetime import date
from datetime import timedelta


def date_range(from_date: date, to_date: date):
    days_range = range((to_date - from_date).days + 1)
    return list(reversed([to_date - timedelta(days=days) for days in days_range]))
