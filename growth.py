""" This script calculates month-to-month percent changes of the closing price S&P 500 Index"""
import csv
import matplotlib.pyplot as plot
import numpy

CHANGES = list()

with open('^GSPC.csv', 'r') as f:
    READER = csv.DictReader(f)
    PREVIOUS_CLOSE = 0
    for row in READER:
        if PREVIOUS_CLOSE != 0:
            CHANGES.append((float(row['Close']) - PREVIOUS_CLOSE) / PREVIOUS_CLOSE)
        PREVIOUS_CLOSE = float(row['Close'])

print("Mean:", numpy.mean(CHANGES))
print("Standard deviation:", numpy.std(CHANGES))
plot.hist(CHANGES, bins=20)
# On Linux ensure python tk is installed.
# https://stackoverflow.com/questions/56656777/userwarning-matplotlib-is-currently-using-agg-which-is-a-non-gui-backend-so
plot.show()

# def optimize(balance=None,
#         monthly_growth_rate_mean=None,
#         monthly_growth_rate_standard_deviation=None,
#         years=None,
#         minimum_discretionary_spending=None,
#         maximum_discretionary_spending=None):