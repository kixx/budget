from typing   import List, Dict, Optional
from datetime import date, datetime, timedelta, time
from decimal  import getcontext, Decimal

DateSpan = List[date]

datetime_format = '%m.%d.%Y %H:%M:%S'

class DailyItem:
    """Budget details for a particular day"""
    def __init__(self, time: time, budget: Decimal):
        self.items   = {}
        self.maximum = Decimal('-Infinity')
        self.add(time, budget)

    def add(self, time, budget) -> None:
        self.items[time] = budget
        if budget > self.maximum:
            self.maximum = budget

class DailyBudget:
    """Unrolled budget per days"""
    def __init__(self):
        self.days   = {}
        self.months = {}

        self._last_max = Decimal(0)


    def add_budget_item(self, dt: datetime, budget: Decimal) -> None:
        date = dt.date()
        if date in self.days:
            self.days[date].add(dt.time(), budget)
        else:
            self.days[date] = DailyItem(dt.time(), budget)
        self._last_max = self.days[date].maximum

    def add_day(self, date) -> None:
        self.days[date] = DailyItem(time.fromisoformat('00:00:00'), self._last_max)

    def compute_month_totals(self) -> None:
        for day in self.days.keys():
            month = day.strftime("%Y-%m")
            if month not in self.months:
                self.months[month] = 0
            self.months[month] += self.days[day].maximum

class Budget:
    """Budget for a period"""

    def __init__(self):
        self.items   = {}
        self.dt_iter = None

    @classmethod
    def from_item_dict(cls, item_dict: dict):
        obj = cls()
        for key, val in item_dict.items():
            dt     = datetime.strptime(key, datetime_format)
            budget = Decimal(val)
            budget.normalize()
            obj.items[dt] = budget
        obj.init_dt_iter()
        return obj

    def init_dt_iter(self) -> None:
        self.dt_iter = iter(sorted(self.items.keys()))

    def date_span(self):
        dt_list = sorted(self.items.keys())
        if len(dt_list) > 0:
            from_dt, to_dt = [dt_list[0], dt_list[-1]]
            cur_date = from_dt.date()
            yield cur_date
            while cur_date < to_dt.date():
                cur_date += timedelta(days = 1)
                yield cur_date

    def get_dates(self) -> DateSpan:
        return list(self.date_span())

    def get_items_by_date(self, date) -> Dict:
        return { dt: self.items[dt] for dt in self.items.keys() if dt.date() == date }

    def daily_budget(self) -> DailyBudget:
        daily = DailyBudget()
    
        day = None
        for dt in self.dt_iter:
            if day is None:
                day = dt.date()
           
            delta = dt.date() - day
            if delta.days == 0: # same day - NOOP
                pass
            else:               # other day - advance day tracker and add potential missing days
                for i in range(delta.days):
                    day += timedelta(days = 1)
                    if day != dt.date():
                        daily.add_day( day )

            daily.add_budget_item(dt, self.items[dt])

        return daily

class Simulator:
    """Simulate costs based on daily budgets"""

    def __init__(self, daily: DailyBudget):
        self.daily   = daily
        self.costs   = {}

