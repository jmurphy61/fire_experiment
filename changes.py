""" This script calculates month-to-month percent changes of the closing price S&P 500 Index"""
import csv
import matplotlib.pyplot as plot
import numpy

def main():
    """ Main function of module """
    changes = list()

    with open('^GSPC.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        previous_close = 0
        for row in reader:
            if previous_close != 0:
                changes.append((float(row['Close']) - previous_close) / previous_close)
            previous_close = float(row['Close'])

    print("Mean:", numpy.mean(changes))
    print("Standard deviation:", numpy.std(changes))
    plot.hist(changes, bins=20)
    # On Linux ensure python tk is installed.
    # https://stackoverflow.com/questions/56656777/userwarning-matplotlib-is-currently-using-agg-which-is-a-non-gui-backend-so
    plot.show()