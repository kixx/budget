from typing   import List, Dict, Optional
from datetime import date, datetime, timedelta, time
from decimal  import getcontext, Decimal

import collections

DailyPlanItem = collections.namedtuple('DailyPlanItem', 'budget cost')

DateSpan = List[date]

DATETIME_FORMAT     = '%m.%d.%Y %H:%M:%S'
MONTHLY_KEY_FORMAT  = '%Y-%m'
DAILY_BUDGET_FACTOR = Decimal(2)

class DailyBudgetItem:
    """Budget details for a particular day"""
    def __init__(self):
        self.items   = {}
        self.maximum = Decimal('-Infinity')

    def add(self, time: time, budget: Decimal) -> None:
        self.items[time] = budget
        if budget > self.maximum:
            self.maximum = budget

class DailyCostItem:
    """Cost details for a particular day"""

    def __init__(self):
        self.items = {}
        self.total = Decimal(0)

    def add(self, time: time, cost: Decimal) -> None:
        self.items[time] = cost
        self.total += cost


class DailyPlan:
    """Unrolled budget and costs per days"""
    def __init__(self):
        self.days   = {}
        self.months = {}

        self._last_max = Decimal(0)


    def add_budget_item(self, dt: datetime, budget: Decimal) -> None:
        date = dt.date()
        if date not in self.days:
            self.days[date] = DailyPlanItem(budget = DailyBudgetItem(), cost = DailyCostItem())
        self.days[date].budget.add(dt.time(), budget)
        self._last_max = self.days[date].budget.maximum

    def add_day(self, date: date) -> None:
        self.days[date] = DailyPlanItem(budget = DailyBudgetItem(), cost = DailyCostItem())
        self.days[date].budget.add(time.fromisoformat('00:00:00'), self._last_max)

    def get_daily_limit(self, dt: datetime) -> Decimal:
        budget = self.days[dt.date()].budget
        matched_time = next((time for time in sorted(budget.items.keys()) if dt.time() >= time), None)
        if matched_time is None:
            prev_date = dt.date() - timedelta(days = 1)
            cur_budget = self.days[prev_date].budget.maximum
        else:
            cur_budget = budget.items[matched_time]

        return cur_budget * DAILY_BUDGET_FACTOR


    def compute_month_totals(self) -> None:
        for day in self.days.keys():
            month = day.strftime(MONTHLY_KEY_FORMAT)
            if month not in self.months:
                self.months[month] = { 'budget': Decimal(0), 'costs' : Decimal(0) }
            self.months[month]['budget'] += self.days[day].budget.maximum

    def add_monthly_cost(self, dt: datetime, cost: Decimal) -> None:
        month = dt.strftime(MONTHLY_KEY_FORMAT)
        self.months[month]['costs'] += cost

    def get_monthly_limit(self, dt: datetime) -> Decimal:
        month = dt.strftime(MONTHLY_KEY_FORMAT)
        return self.months[month]['budget'] - self.months[month]['costs']

class Budget:
    """Budget for a period"""

    def __init__(self):
        self.items   = {}
        self.dt_iter = None

    @classmethod
    def from_item_dict(cls, item_dict: dict):
        obj = cls()
        for key, val in item_dict.items():
            dt     = datetime.strptime(key, DATETIME_FORMAT)
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

    def compute_daily_plan(self) -> DailyPlan:
        daily = DailyPlan()
    
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

    def __init__(self, daily: DailyPlan):
        self.daily   = daily
        self.costs   = {}

