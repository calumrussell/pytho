import pandas as pd
from pandas.core.frame import DataFrame
from typing import List, Dict, Tuple

from api.models import Coverage
from helpers import prices
from helpers.prices.data import DataSource, SourceFactory
from .base import (
    AlatorPerformanceOutput,
    AlatorClientInput,
    AlatorUnusableInputException,
)
from panacea import fixedweight_backtest, BacktestInput


class FixedSignalBackTestWithPriceAPI:
    """Initialises and loads the data to be used by the backtest.

    Doesn't test for malformed input as all of the input tests are carried out in
    the API front end

    Attributes
    ---------
    weights: `List[float]`
    coverage: `List[Coverage]`
    signal: `Dict[str, float]`
    results: `AlatorPerformanceOutput`

    Raises
    ---------
    AlatorUnusableInputException
        Valid input but some data is missing
    ConnectionError
        Failed to connect to InvestPySource
    """

    def run(self) -> None:
        price_request = prices.PriceAPIRequests(self.coverage)
        try:
            bt_sources = price_request.get_overlapping()
        except Exception:
            raise AlatorUnusableInputException

        dates = None
        close = {}
        for source in bt_sources:
            if dates == None:
                dates = list(bt_sources[source].get_dates())
            close[str(source)] = bt_sources[source].get_close()["Close"].to_list()

        if not close:
            raise AlatorUnusableInputException

        coverage_ids = [str(c.id) for c in self.coverage]

        bt_in = BacktestInput(
            assets=coverage_ids,
            dates=dates,
            weights=self.signal,
            close=close,
        )

        bt = fixedweight_backtest(bt_in)
        self.results = AlatorPerformanceOutput(
            ret=bt[0] * 100,
            cagr=bt[1] * 100,
            vol=bt[2] * 100,
            mdd=bt[3] * 100,
            sharpe=bt[4],
            values=bt[5],
            returns=bt[6],
            dates=bt[7],
        )
        return

    def __init__(self, alator: AlatorClientInput):
        self.weights: List[float] = alator["weights"]
        try:
            self.coverage: List[Coverage] = Coverage.objects.filter(
                id__in=alator["assets"]
            )
        except ValueError:
            raise AlatorUnusableInputException

        if not self.coverage:
            raise AlatorUnusableInputException

        if len(self.coverage) != len(alator["assets"]):
            raise AlatorUnusableInputException

        self.signal: Dict[str, float] = {
            str(i): j for (i, j) in zip(alator["assets"], self.weights)
        }
        return
