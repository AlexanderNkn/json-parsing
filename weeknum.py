from datetime import datetime, timedelta


WEEkDAYS = {'ПН': 1, 'ВТ': 2, 'СР': 3, 'ЧТ': 4, 'ПТ': 5, 'СБ': 6, 'ВС': 7}


class CustomizedCalendar:
    def __init__(self, start_week=None):
        self.start_week = 'ПН 00:00' if start_week is None else start_week
        self.start_weekday = WEEkDAYS[self.start_week.split()[0]]
        self.start_hour = int(self.start_week.split()[1].split(':')[0])
        self.start_min = int(self.start_week.split()[1].split(':')[1])

    def _get_week_start(self, date):
        """Метод получает дату старта первой недели.

        Находим дату первого четверга в году и отнимаем от нее разницу
        между четвергом в неделе и новым стартом недели."""
        year = date.year
        first_th = datetime.fromisocalendar(year, 1, 4)
        delta = timedelta(days=4) - timedelta(
            days=self.start_weekday,
            hours=self.start_hour,
            minutes=self.start_min,
        )
        # доп. проверка, чтобы старт всегда был раньше четверга
        if delta.total_seconds() >= 0:
            return first_th - delta
        return first_th - (timedelta(days=7) + delta)

    def get_correct_week_start(self, date):
        """Две проверки

        1. Если проверяемая дата идет раньше начала первой недели в году,
        нужно сделать перерассчет так, чтобы первая неделя начиналась
        год назад
        2. Последние несколько дней могут входить в первую неделю
        следующего года."""
        correct = self._get_week_start(date)
        if date < correct:
            date -= timedelta(days=7)
            correct = self._get_week_start(date)
        # первая неделя для следующего года
        next_year = self._get_week_start(datetime(date.year + 1, 1, 1))
        if date >= next_year:
            correct = next_year
        return correct

    def calculate(self, date):
        diff_days = (date - self.get_correct_week_start(date)).total_seconds()
        sec_in_week = 7 * 60 * 60 * 24
        return int(diff_days // sec_in_week) + 1
