"""FIRE simulation"""
import argparse
from .models import Scenario

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
    action='store_true',
    default=False)

def main():
    """Main function for command line utility"""
    args = ARG_PARSER.parse_args()
    print(Scenario(**vars(args)).simulate_many())

if __name__ == '__main__':
    main()