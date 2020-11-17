from datetime import datetime, timedelta

from weeknum import CustomizedCalendar


def test_isocalendar():
    """Вычисление номера недели при нулевом смещении должно
    соответствовать isocalendar()."""
    inst = CustomizedCalendar()
    for year in [2000, 2001, 2002, 2003, 2004, 2005]:
        date = datetime(year, 12, 20)
        for _ in range(20):
            assert inst.calculate(date) == datetime.isocalendar(date)[1]
            date += timedelta(days=1)


def test_time():
    """Проверка смены недели при переходе через заданное время."""
    inst = CustomizedCalendar('ПТ 18:30')
    assert inst.calculate(datetime(2019, 12, 27, 18, 29)) == 52
    assert inst.calculate(datetime(2019, 12, 27, 18, 30)) == 1
    assert inst.calculate(datetime(2020, 1, 3, 18, 29)) == 1
    assert inst.calculate(datetime(2020, 1, 3, 18, 30)) == 2
