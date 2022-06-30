import pandas as pd
from pandas.core.frame import DataFrame
from typing import List, Dict, Tuple

from api.models import Coverage
from helpers import prices
from helpers.prices.data import DataSource, SourceFactory
from .base import (
    BackTest,
    BackTestResults,
    BackTestInvalidInputException,
    BackTestUnusableInputException,
)
from panacea import fixedweight_backtest, BacktestInput


class FixedSignalBackTestWithPriceAPI(BackTest):
    """Initialises and loads the data to be used by the backtest.

    Attributes
    ---------
    assets : `List[str]`
        List of assetids in string format prefixed with 'EQ:`
    weights : `List[float]`
        List of portfolio weights in decimal form.
    price_request : `prices.PriceAPIRequests`
        Object that determines how the request for a Coverage object is fulfilled

    Raises
    ---------
    BackTestInvalidInputException
        Either weights or assets is missing or not formatted
    BackTestUnusableInputException
        Input is valid but there is no data source
    ConnectionError
        Failed to connect to InvestPySource
    """

    def run(self) -> None:
        to_dict: Dict[str, List[float]] = {
            str(i): self.prices[i]["Close"].to_list() for i in self.prices
        }

        bt_in = BacktestInput(
            assets=self.assets,
            dates=self.dates,
            weights=self.signal,
            close=to_dict,
        )

        bt: Tuple[
            float, float, float, float, float, List[float], List[float], List[float]
        ] = fixedweight_backtest(bt_in)

        self.results: BackTestResults = BackTestResults(
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

    def _init_prices(self) -> None:
        self.prices: Dict[int, DataFrame] = {}
        try:
            sources_dict: Dict[int, DataSource] = self.price_request.get()
        # Invalid Input
        except ValueError:
            raise BackTestUnusableInputException
        # Request failed to return 200 status code
        except ConnectionError:
            raise ConnectionError
        # Valid input but query could not produce result
        except RuntimeError:
            raise BackTestUnusableInputException
        # Information was unavailable or not found
        except IndexError:
            raise BackTestUnusableInputException

        else:
            ##If we are missing data, stop here
            for i in sources_dict:
                ##Always returns df, even if we have no source
                check: pd.DataFrame = sources_dict[i].get_prices()
                if check.empty:
                    raise BackTestUnusableInputException
            if not sources_dict:
                raise BackTestUnusableInputException

            date_lists = [set(sources_dict[i].get_dates()) for i in sources_dict]
            self.dates = sorted([int(i) for i in set.intersection(*date_lists)])
            union_dict = {
                i: SourceFactory.find_dates(
                    self.dates, sources_dict[i], sources_dict[i].__class__
                )
                for i in sources_dict
            }

            for i in union_dict:
                ##By this point, we always get a result
                prices: pd.DataFrame = union_dict[i].get_close()
                self.prices[i] = prices

        return

    def __init__(self, assets: List[int], weights: List[float]):
        if not assets or not weights:
            raise BackTestInvalidInputException

        if len(assets) != len(weights):
            raise BackTestInvalidInputException

        self.weights: List[float] = weights

        try:
            self.coverage: List[Coverage] = Coverage.objects.filter(id__in=assets)
        except:
            raise BackTestUnusableInputException

        if len(self.coverage) != len(assets):
            raise BackTestUnusableInputException

        self.assets: List[str] = [str(c.id) for c in self.coverage]
        self.signal: Dict[str, float] = {
            i: j for (i, j) in zip(self.assets, self.weights)
        }
        self.price_request: prices.PriceAPIRequests = prices.PriceAPIRequests(
            self.coverage
        )
        self._init_prices()
        super().__init__(self.prices)
        return
