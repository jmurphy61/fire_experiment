"""FIRE simulation"""
import argparse
import math
import random
from datetime import datetime
from multiprocessing.pool import ThreadPool
import pandas

def sigmoid(logistic_max, logistic_growth_rate, logistic_midpoint, input_value):
    """https://en.wikipedia.org/wiki/Logistic_function"""
    return logistic_max / (1 + math.exp(-logistic_growth_rate * (input_value - logistic_midpoint)))

class Scenario:
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
        self.output_histories = str(kwargs.get('output_histories', False))

    def simulate_once(self, simulation_number) -> dict:
        """Run one simulation"""
        rows_list = list()

        first_row = dict()
        first_row['Starting Balance'] = self.starting_balance
        first_row['Cumulative Inflation Multiplier'] = 1
        first_row['Discretionary Spending'] = (
            self.minimum_discretionary_spending + self.maximum_discretionary_spending
            ) / 2
        first_row['Gross Withdrawal'] = first_row['Discretionary Spending'] / 0.7
        first_row['Growth Rate'] = random.gauss(
            self.monthly_growth_rate_mean,
            self.monthly_growth_rate_std_dev)
        first_row['Growth'] = first_row['Starting Balance'] * first_row['Growth Rate']
        first_row['Net Growth/Loss'] = first_row['Growth'] - first_row['Gross Withdrawal']
        first_row['Ending Balance'] = first_row['Starting Balance'] + first_row['Net Growth/Loss']
        rows_list.append(first_row)

        for month in range(1, self.months):
            row = dict()
            try:
                row['Starting Balance'] = rows_list[month - 1]['Ending Balance']
            except IndexError:
                print('IndexError')
                print('simulation_number', simulation_number)
                print('month', month)
                print('rows_lost', rows_list)
                print('row', row)
                raise IndexError
            row['Cumulative Inflation Multiplier'] = (
                1 + (self.annual_inflation_rate / 12)) ** month
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
            row['Growth Rate'] = random.gauss(
                self.monthly_growth_rate_mean,
                self.monthly_growth_rate_std_dev)
            row['Growth'] = row['Starting Balance'] * row['Growth Rate']
            row['Net Growth/Loss'] = row['Growth'] - row['Gross Withdrawal']
            row['Ending Balance'] = row['Starting Balance'] + row['Net Growth/Loss']
            rows_list.append(row)
            if (row['Ending Balance'] <= 0) and (month < self.months - 1):
                return {
                    'history': rows_list,
                    'success': False
                }
        return {
            'history': rows_list,
            'success': True
        }

    def simulate(self) -> dict:
        """Generate the specified number of years in a simulation of a FIRE situation
        based on the provided parameters"""

        failures = 0
        history_writer = pandas.ExcelWriter(f'histories_{datetime.now().isoformat()}.xlsx') # pylint: disable=abstract-class-instantiated

        # for simulation in range(simulations):
        #     result = simulate_once(simulation)
        with ThreadPool(4) as pool:
            for simulation_number, result in enumerate(
                    pool.map(self.simulate_once, range(self.simulations))):
                if result['success'] is False:
                    failures +=1
                if self.output_histories == 'True':
                    pandas.DataFrame(result['history']).to_excel(history_writer, str(simulation_number))

        if scenario.output_histories == 'True':
            history_writer.save()
        return {
            "Simulations": self.simulations,
            "Successes": self.simulations - failures,
            "Failures": failures,
            "Success Rate": (self.simulations - failures) / self.simulations,
            "Failures Rate": failures / self.simulations
        }

ARG_PARSER = argparse.ArgumentParser()
ARG_PARSER.add_argument(
    '--simulations',
    dest='simulations',
    default=1000)
ARG_PARSER.add_argument(
    '--months',
    dest='months',
    default=360)
ARG_PARSER.add_argument(
    '--starting-balance',
    dest='starting_balance',
    default=1e6)
ARG_PARSER.add_argument(
    '--monthly-growth-rate-mean',
    dest='monthly_growth_rate_mean',
    default=0.0061)
ARG_PARSER.add_argument(
    '--monthly-growth-rate-std-dev',
    dest='monthly_growth_rate_std_dev',
    default=0.0537)
ARG_PARSER.add_argument(
    '--annual-inflation-rate',
    dest='annual_inflation_rate',
    default=0.02)
ARG_PARSER.add_argument(
    '--minimum-discretionary-spending',
    dest='minimum_discretionary_spending',
    default=2000)
ARG_PARSER.add_argument(
    '--maximum-discretionary-spending',
    dest='maximum_discretionary_spending',
    default=4000)
ARG_PARSER.add_argument(
    '--output-histories',
    dest='output_histories',
    default=False)

if __name__ == '__main__':
    args = ARG_PARSER.parse_args()
    scenario = Scenario(**vars(args))
    print(scenario.simulate())
