from panacea import AlatorInput, alator_backtest

from api.models import Coverage
from helpers import prices

from .base import (
    AlatorClientInput,
    AlatorPerformanceOutput,
    AlatorUnusableInputException,
)


class FixedSignalBackTestWithPriceAPI:
    """Initialises and loads the data to be used by the backtest.

    Doesn't test for malformed input as all of the input tests are carried out in
    the API front end

    Attributes
    ---------
    weights: `List[float]`
    coverage: `QuerySet[Coverage]`
    signal: `Dict[str, float]`
    results: `AlatorPerformanceOutput`

    Raises
    ---------
    AlatorUnusableInputException
        Valid input but some data is missing
    ConnectionError
        Failed to connect to InvestPySource
    """

    def run(self):
        price_request = prices.PriceAPIRequests(self.coverage)
        try:
            bt_sources = price_request.get_overlapping()
        except Exception as exc:
            raise AlatorUnusableInputException from exc

        dates = None
        close = {}
        for source in bt_sources:
            if dates is None:
                dates = list(bt_sources[source].get_dates())
            close[str(source)] = bt_sources[source].get_close()["Close"].to_list()

        if not close:
            raise AlatorUnusableInputException

        coverage_ids = [str(c.id) for c in self.coverage]

        if dates:
            bt_in = AlatorInput(
                assets=coverage_ids,
                dates=dates,
                weights=self.signal,
                close=close,
            )
        else:
            raise AlatorUnusableInputException

        bt_res = alator_backtest(bt_in)
        self.results = AlatorPerformanceOutput(
            ret=bt_res[0] * 100,
            cagr=bt_res[1] * 100,
            vol=bt_res[2] * 100,
            mdd=bt_res[3] * 100,
            sharpe=bt_res[4],
            values=bt_res[5],
            returns=bt_res[6],
            dates=bt_res[7],
        )
        return

    def __init__(self, alator: AlatorClientInput):
        self.weights = alator["weights"]
        try:
            self.coverage = Coverage.objects.filter(id__in=alator["assets"])
        except ValueError:
            raise AlatorUnusableInputException

        if not self.coverage:
            raise AlatorUnusableInputException

        if len(self.coverage) != len(alator["assets"]):
            raise AlatorUnusableInputException

        self.signal = {str(i): j for (i, j) in zip(alator["assets"], self.weights)}
        self.results = None
        return
