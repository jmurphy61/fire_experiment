"""Conceptual models related to FIRE"""
import os
import random
from datetime import datetime
from multiprocessing.pool import ThreadPool
import pandas
from .utilities import sigmoid
from . import data

class Scenario:
    """Constraints for a potential FIRE lifestyle, and simulation functionality."""
    def __init__(self, **kwargs):
        self.simulations = int(kwargs.get('simulations', 1000))
        self.months = int(kwargs.get('months', 360))
        self.starting_balance = float(kwargs.get('starting_balance', 1e6))
        self.annual_inflation_rate = float(kwargs.get('annual_inflation_rate', 0.02))
        self.monthly_growth_rate_std_dev = float(kwargs.get('monthly_growth_rate_std_dev', 0.0537))
        self.monthly_growth_rate_mean = float(kwargs.get('monthly_growth_rate_mean', 0.0061))
        self.minimum_discretionary_spending = float(
            kwargs.get('minimum_discretionary_spending', 2000))
        self.maximum_discretionary_spending = float(
            kwargs.get('maximum_discretionary_spending', 4000))
        self.output_histories = bool(kwargs.get('output_histories', False))

    def simulate(self, _) -> dict:
        """Run one simulation"""
        rows_list = list()

        first_row = {
            'Starting Balance': self.starting_balance,
            'Cumulative Inflation Multiplier': 1,
            'Discretionary Spending': (
                self.minimum_discretionary_spending + self.maximum_discretionary_spending) / 2,
            'Growth Rate': random.gauss(
                self.monthly_growth_rate_mean,
                self.monthly_growth_rate_std_dev)
        }
        first_row['Gross Withdrawal'] = first_row['Discretionary Spending'] / 0.7
        first_row['Growth'] = first_row['Starting Balance'] * first_row['Growth Rate']
        first_row['Net Growth/Loss'] = first_row['Growth'] - first_row['Gross Withdrawal']
        first_row['Ending Balance'] = first_row['Starting Balance'] + first_row['Net Growth/Loss']
        rows_list.append(first_row)

        for month in range(1, self.months):
            row = {
                'Starting Balance': rows_list[month - 1]['Ending Balance'],
                'Cumulative Inflation Multiplier': (
                    1 + (self.annual_inflation_rate / 12)) ** month,
                'Growth Rate': random.gauss(
                    self.monthly_growth_rate_mean,
                    self.monthly_growth_rate_std_dev)
            }
            try:
                row['Discretionary Spending'] = (
                    sigmoid(
                        logistic_max=self.maximum_discretionary_spending\
                            - self.minimum_discretionary_spending,
                        logistic_growth_rate=0.1,
                        logistic_midpoint=0,
                        input_value=(
                            rows_list[month - 1]['Growth'] - first_row['Discretionary Spending']
                            )/ first_row['Discretionary Spending']
                        ) + self.minimum_discretionary_spending\
                    if row['Starting Balance'] > 1e6 else self.minimum_discretionary_spending\
                    ) * row['Cumulative Inflation Multiplier']
            except OverflowError:
                row['Discretionary Spending'] = self.maximum_discretionary_spending
            row['Gross Withdrawal'] = row['Discretionary Spending'] / 0.7
            row['Growth'] = row['Starting Balance'] * row['Growth Rate']
            row['Net Growth/Loss'] = row['Growth'] - row['Gross Withdrawal']
            row['Ending Balance'] = row['Starting Balance'] + row['Net Growth/Loss']
            rows_list.append(row)
            if (row['Ending Balance'] <= 0) and (month < self.months - 1):
                return rows_list
        return rows_list

    def simulate_many(self) -> dict:
        """Generate the specified number of years in a simulation of a FIRE situation
        based on the provided parameters"""

        failures = 0
        # https://stackoverflow.com/questions/59983765/pandas-abstract-class-excelwriter-with-abstract-methods-instantiatedpylint-p
        if self.output_histories:
            history_writer = pandas.ExcelWriter( # pylint: disable=abstract-class-instantiated
                os.path.join(
                    os.path.dirname(data.__file__),
                    f'histories_{datetime.now().isoformat()}.xlsx'
                ))

        with ThreadPool(4) as pool:
            for simulation_number, history in enumerate(
                    pool.map(self.simulate, range(self.simulations))):
                if len(history) < self.months:
                    failures += 1
                    evaluation = 'Failure'
                else:
                    evaluation = 'Success'
                if self.output_histories:
                    pandas.DataFrame(history).to_excel(
                        history_writer,
                        f'{simulation_number + 1} {evaluation}')

        if self.output_histories:
            history_writer.save()
        return {
            "Simulations": self.simulations,
            "Successes": self.simulations - failures,
            "Failures": failures,
            "Success Rate": (self.simulations - failures) / self.simulations,
            "Failures Rate": failures / self.simulations
        }
