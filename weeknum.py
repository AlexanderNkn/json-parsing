from datetime import datetime, timedelta


WEEkDAYS = {'ПН': 1, 'ВТ': 2, 'СР': 3, 'ЧТ': 4, 'ПТ': 5, 'СБ': 6, 'ВС': 7}


class CustomizedCalendar:
    def __init__(self, start_week=None):
        self.start_week = 'ПН 00:00' if start_week is None else start_week
        self.start_weekday = WEEkDAYS[self.start_week.split()[0]]
        self.start_hour = int(self.start_week.split()[1].split(':')[0])
        self.start_min = int(self.start_week.split()[1].split(':')[1])

    def get_week_start(self, date):
        delta = date.isoweekday() - self.start_weekday
        return date - timedelta(
            days=delta % 7, hours=self.start_hour, minutes=self.start_min
        )

    def get_week_indicator(self, date):
        week_start = self.get_week_start(date)
        return week_start + timedelta(days=3)

    def get_first_week(self, year):
        indicator_date = self.get_week_indicator(datetime(year, 1, 1))
        if indicator_date.year == year:  # The date "year.1.1" is on 1st week.
            return self.get_week_start(datetime(year, 1, 1))
        else:  # The date "year.1.1" is on the last week of "year-1".
            return self.get_week_start(datetime(year, 1, 8))

    def calculate(self, date):
        year = self.get_week_indicator(date).year
        first_date_of_first_week = self.get_first_week(year)
        diff_days = (date - first_date_of_first_week).days
        return diff_days // 7 + 1
