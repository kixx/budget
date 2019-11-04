from decimal  import Decimal
from datetime import date, datetime, time

from budget   import Budget, Simulator

import pytest
import pprint

pp = pprint.PrettyPrinter(indent=4)

@pytest.fixture
def basic_item_dict():
    return {
        '01.01.2019 00:00:00': '07.00',
        '01.04.2019 00:00:00': '00.00',
        '01.07.2019 00:00:00': '100.50',
    }

@pytest.fixture
def date_dict():
    return {
        '01.01.2020 00:00:00': 0,
        '01.31.2020 00:00:00': 0,
    }

@pytest.fixture
def many_items_per_day():
    return {
        '01.01.2020 00:00:00': 0,
        '01.01.2020 00:30:00': 0,
        '01.01.2020 06:00:00': 0,
        '01.15.2020 12:00:00': 0,
        '01.15.2020 06:30:00': 0,
        '01.31.2020 00:00:00': 0,
    }

@pytest.fixture
def date_item_count():
    return {
        '2020-01-01': 3,
        '2020-01-15': 2,
        '2020-01-31': 1,
    }

@pytest.fixture
def one_item_dict():
    return {
        '2020-01-01': 1,
    }

@pytest.fixture
def complex_item_dict():
    return {
        '01.01.2019 00:00:00': '07.00',
        '01.01.2019 00:30:00': 0,
        '01.01.2019 16:00:00': '1.35',
        '01.01.2019 22:00:00': '06.00',
        '01.05.2019 13:00:00': 2,
        '01.06.2019 06:30:00': 0,
        '01.09.2019 00:00:00': '100.50',
    }

# Budget Tests
class TestBudget:
    def test_from_dict(self, basic_item_dict):
        budget = Budget.from_item_dict(basic_item_dict)
        assert isinstance(budget, Budget)
        assert len(budget.items.keys()) == 3

    def test_decimal(self, basic_item_dict):
        budget = Budget.from_item_dict(basic_item_dict)
        some_money = Decimal('7')
        assert some_money in budget.items.values()

        big_money = Decimal('100.5')
        assert big_money in budget.items.values()
        
        zero_money = Decimal('0')
        assert zero_money in budget.items.values()

    def test_date_span(self, date_dict):
        budget = Budget.from_item_dict(date_dict)
        date_span = budget.get_dates()
        assert(len(date_span) == 31)

    def test_item_date_filter(self, many_items_per_day, date_item_count):
        budget = Budget.from_item_dict(many_items_per_day)
        for budget_date, item_count in date_item_count.items():
            items = budget.get_items_by_date(date.fromisoformat(budget_date))
            assert len(items.keys()) == item_count

    def test_budget_items(self, complex_item_dict):
        budget = Budget.from_item_dict(complex_item_dict)
        daily = budget.compute_daily_plan()

        assert len(daily.days.keys()) == 9

        long_day = daily.days[date.fromisoformat('2019-01-01')]
        assert len(long_day.budget.items) == 4
        assert long_day.budget.maximum == Decimal(7)
        
        before_next_change = daily.days[date.fromisoformat('2019-01-04')]
        assert before_next_change.budget.maximum == Decimal(7)
        
        change_day = daily.days[date.fromisoformat('2019-01-05')]
        assert len(change_day.budget.items) == 1
        assert change_day.budget.maximum == Decimal(2)

        pause_day = daily.days[date.fromisoformat('2019-01-06')]
        assert pause_day.budget.maximum == Decimal(0)

        before_last = daily.days[date.fromisoformat('2019-01-08')]
        assert before_last.budget.maximum == Decimal(0)

        last_day = daily.days[date.fromisoformat('2019-01-09')]
        assert last_day.budget.maximum == Decimal('100.5')

        jan_budget = daily.months['2019-01']['budget']
        assert jan_budget == Decimal('130.5')

    def test_monthly_limits(self, complex_item_dict):
        budget = Budget.from_item_dict(complex_item_dict)
        daily = budget.compute_daily_plan()
        
        monthly_limit = daily.get_monthly_limit(date.fromisoformat('2019-01-09'))
        assert monthly_limit == Decimal('130.5')

        daily.add_monthly_cost(datetime.fromisoformat('2019-01-09T00:00:00'), Decimal('30.5'))
        monthly_limit = daily.get_monthly_limit(date.fromisoformat('2019-01-09'))
        assert monthly_limit == Decimal('100')

    def test_daily_limits(self, complex_item_dict):
        budget = Budget.from_item_dict(complex_item_dict)
        daily = budget.compute_daily_plan()
        
        daily_limit = daily.get_daily_limit(datetime.fromisoformat('2019-01-05T08:00:00'))
        assert daily_limit == Decimal('14')
        
        daily_limit = daily.get_daily_limit(datetime.fromisoformat('2019-01-05T13:00:00'))
        assert daily_limit == Decimal('4')

    def test_simulator(self, complex_item_dict):
        budget = Budget.from_item_dict(complex_item_dict)
        sim = Simulator(budget)
        sim.generate_costs()
        for day in sim.daily.days.keys():
            pp.pprint({ 'date': day.strftime("%d.%m.%Y") , 'max': sim.daily.days[day].budget.maximum, 'total': sim.daily.days[day].cost.total }) 

