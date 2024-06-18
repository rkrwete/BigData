# Линейная регресия

import pandas as pd
import numpy as np

def linear_regression(first_values, second_values):
    first_mean = np.mean(first_values)
    second_mean = np.mean(second_values)

    numerator = sum((first_values - first_mean) * (second_values - second_mean))
    denominator = sum((first_values - first_mean) ** 2)

    b_1 = numerator / denominator
    b_0 = second_mean - b_1 * first_mean

    result = b_0 + b_1 * first_values
    
    return result