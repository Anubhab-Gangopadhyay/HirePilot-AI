from functools import lru_cache

import numpy as np
from sklearn.linear_model import LinearRegression


class RegressionBundle:
    def __init__(self, features: np.ndarray, targets: np.ndarray):
        self.model = LinearRegression()
        self.model.fit(features, targets)

    def predict(self, values: list[float]) -> float:
        prediction = self.model.predict([values])[0]
        return float(round(prediction, 2))


@lru_cache(maxsize=1)
def load_models() -> dict[str, RegressionBundle]:
    price_features = np.array([
        [20000, 2.8, 6.5, 6.8, 7.5],
        [50000, 4.1, 7.1, 7.2, 8.2],
        [80000, 5.6, 7.8, 7.6, 8.8],
        [120000, 6.4, 8.4, 8.1, 9.1],
        [250000, 7.1, 8.8, 8.5, 9.2]
    ])
    price_targets = np.array([18000, 42000, 76000, 130000, 265000])

    roi_features = np.array([
        [50000, 80000, 3.2, 1.5, 1200],
        [100000, 160000, 4.0, 2.0, 1500],
        [180000, 240000, 5.1, 2.8, 2000],
        [250000, 420000, 5.8, 3.3, 2500]
    ])
    roi_targets = np.array([1.4, 1.9, 2.6, 3.2])

    income_features = np.array([
        [25000, 3.0, 2, 15000],
        [60000, 4.5, 3, 35000],
        [100000, 5.8, 4, 55000],
        [180000, 6.8, 5, 90000]
    ])
    income_targets = np.array([35000, 105000, 220000, 430000])

    return {
        "price": RegressionBundle(price_features, price_targets),
        "roi": RegressionBundle(roi_features, roi_targets),
        "income": RegressionBundle(income_features, income_targets)
    }
