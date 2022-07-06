from typing import Dict
from django.test import SimpleTestCase
import pandas as pd

from helpers.prices import InvestPySource
from helpers.prices.data import FakeData

from ..riskattribution import (
    BootstrapRiskAttributionAlt,
    RiskAttribution,
    RollingRiskAttribution,
    BootstrapRiskAttribution,
    WindowLengthError,
    RiskAttributionUnusableInputException,
    RollingRegressionInput,
    RegressionInput,
)


def get_data() -> Dict[int, InvestPySource]:
    res: Dict[int, InvestPySource] = {}
    res[0] = FakeData.get_investpy(1, 0.1, 1000)
    res[1] = FakeData.get_investpy(2, 0.2, 1000)
    return res


class TestBootstrapRiskAttributionAlt(SimpleTestCase):
    def setUp(self):
        self.data: Dict[int, InvestPySource] = get_data()
        return

    def test_that_bootstrap_loads(self):
        ra = BootstrapRiskAttributionAlt(
            RegressionInput(dep=0, ind=[1]), data=self.data
        )
        res = ra.run()
        return


class TestBootstrapRiskAttribution(SimpleTestCase):
    def setUp(self):
        self.data: Dict[int, InvestPySource] = get_data()
        return

    def test_that_bootstrap_loads(self):
        ra = BootstrapRiskAttribution(
            RollingRegressionInput(
                dep=0,
                ind=[1],
                window=5,
            ),
            data=self.data,
        )
        res = ra.run()
        return


class TestRollingRiskAttribution(SimpleTestCase):
    def setUp(self):
        self.data = get_data()
        return

    def test_that_rolling_risk_attribution_loads(self):
        ra = RollingRiskAttribution(
            RollingRegressionInput(
                dep=0,
                ind=[1],
                window=5,
            ),
            data=self.data,
        )
        res = ra.run()
        return

    def test_that_error_is_thrown_with_window_longer_than_data(self):
        with self.assertRaises(WindowLengthError) as context:
            ra = RollingRiskAttribution(
                RollingRegressionInput(
                    dep=0,
                    ind=[1],
                    window=99999999,
                ),
                data=self.data,
            )
            res = ra.run()
        return

    def test_that_dates_is_same_length_as_data_and_valid(self):
        last = self.data[0].get_dates()[-1]
        ra = RollingRiskAttribution(
            RollingRegressionInput(
                dep=0,
                ind=[1],
                window=5,
            ),
            data=self.data,
        )
        res = ra.run()
        self.assertTrue(len(res["dates"]) == len(res["regressions"]))
        self.assertTrue(last in res["dates"])
        return

    def test_that_rolling_riskattribution_works_with_factor_source(self):
        self.data[3] = FakeData.get_factor(1, 0.1, 100)
        ra = RollingRiskAttribution(
            RollingRegressionInput(
                dep=0,
                ind=[3],
                window=5,
            ),
            data=self.data,
        )
        res = ra.run()
        return


class TestRiskAttribution(SimpleTestCase):
    def setUp(self):
        self.data = get_data()
        return

    def test_that_risk_attribution_loads(self):
        ra = RiskAttribution(
            RegressionInput(
                dep=0,
                ind=[1],
            ),
            data=self.data,
        )
        res = ra.run()
        regression = res["regression"]
        self.assertTrue(regression)
        self.assertTrue(len(regression["coefficients"]) == 1)
        self.assertTrue(regression["intercept"])
        self.assertTrue(res["avgs"])
        return


class TestRiskAttributionBase(SimpleTestCase):
    def setUp(self):
        self.data = get_data()
        return

    def test_that_throws_error_when_dates_dont_overlap(self):
        idx = pd.Index(
            data=[pd.Timestamp(2000, 1, 1), pd.Timestamp(2000, 1, 2)], name="Date"
        )
        idx1 = pd.Index(
            data=[pd.Timestamp(2001, 1, 1), pd.Timestamp(2001, 1, 2)], name="Date"
        )

        df = pd.DataFrame({"Close": [1, 2], "Open": [1, 2]}, index=idx)
        df1 = pd.DataFrame({"Close": [1, 2], "Open": [1, 2]}, index=idx1)
        data = {0: InvestPySource(df), 1: InvestPySource(df1)}
        reg_input = RegressionInput(
            dep=0,
            ind=[1],
        )
        self.assertRaises(
            RiskAttributionUnusableInputException, RiskAttribution, reg_input, data
        )
        return

    def test_that_error_thrown_with_invalid_inputs(self):
        reg_input = RegressionInput(
            dep=0,
            ind=[10],
        )

        self.assertRaises(
            RiskAttributionUnusableInputException,
            RiskAttribution,
            reg_input,
            self.data,
        )

    def test_that_get_windows_produces_valid_number_of_windows(self):
        ra = RiskAttribution(
            RegressionInput(
                dep=0,
                ind=[1],
            ),
            data=self.data,
        )
        count = 0
        window_length = 5
        windows = ra.get_windows(window_length)
        for ind, dep in windows:
            count += 1
        expected_length = len(ra.ind_data) - 5
        self.assertTrue(count == expected_length)
        return
