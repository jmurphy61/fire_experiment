"""Useful functions to be used when simulating FIRE scenarios."""
import math

def sigmoid(logistic_max, logistic_growth_rate, logistic_midpoint, input_value):
    """https://en.wikipedia.org/wiki/Logistic_function"""
    return logistic_max / (1 + math.exp(-logistic_growth_rate * (input_value - logistic_midpoint)))
