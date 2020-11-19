from datetime import datetime, timedelta


class CustomizedCalendar:
    """Класс меняет день и время начала недели в ISO календаре."""

    WEEKDAYS = {'ПН': 1, 'ВТ': 2, 'СР': 3, 'ЧТ': 4, 'ПТ': 5, 'СБ': 6, 'ВС': 7}

    def __init__(self, start_week=None):
        self.start_week = 'ПН 00:00' if start_week is None else start_week
        start_weekday, week_time = self.start_week.split()
        self.start_weekday = CustomizedCalendar.WEEKDAYS[start_weekday]
        self.start_hour, self.start_min = map(int, week_time.split(':'))

    def _get_week_start(self, date):
        """Метод возвращает дату начала первой недели БЕЗ учета даты, для
        которой вычисляется номер недели.

        Метод находит дату первого четверга в году, и исходяи из нее и
        пользовательского начала недели, возвращает дату начала первой недели.
        """
        year = date.year
        first_thursday = datetime.fromisocalendar(year, 1, 4)
        offset = timedelta(days=4) - timedelta(
            days=self.start_weekday,
            hours=self.start_hour,
            minutes=self.start_min,
        )
        # дата начала первой недели должна быть всегда раньше первого четверга
        if offset.total_seconds() >= 0:
            return first_thursday - offset
        return first_thursday - (timedelta(days=7) + offset)

    def get_correct_week_start(self, date):
        """Метод возвращает дату начала первой недели С учетом даты, для
        которой вычисляется номер недели.

        Метод проверяет, не попала ли дата, находящаяся в конце года, в
        первую неделю следующего года, либо наоброт, дата в начале года в
        последнюю неделю предыдущего года.
        """
        correct = self._get_week_start(date)
        if date < correct:
            return self._get_week_start(datetime(date.year - 1, 1, 1))
        next_year = self._get_week_start(datetime(date.year + 1, 1, 1))
        if date >= next_year:
            correct = next_year
        return correct

    def calculate(self, date):
        diff_days = (date - self.get_correct_week_start(date)).total_seconds()
        sec_in_week = 7 * 60 * 60 * 24
        return int(diff_days // sec_in_week) + 1
