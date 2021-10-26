import numpy as np
import numpy.typing as npt
import pandas as pd
import statsmodels.api as sm
from typing import Any, Callable, Dict, List, Tuple, TypedDict

from helpers.portfolio.calculator.calcs.main import (
    max_dd_threshold_position,
)
from helpers.prices import FactorSource
from helpers.prices.data import DataSource

from .riskattribution import (
    RegressionCoefficient,
    RegressionResult,
    RiskAttributionDefinition,
)


class HistoricalDrawdownEstimatorNoFactorSourceException(Exception):
    def __init__(self) -> None:
        super().__init__()


class HistoricalDrawdownEstimatorFactorDataFormatter:
    @staticmethod
    def format(data: pd.DataFrame) -> pd.DataFrame:
        data["period"] = pd.to_datetime(data.index, unit="s")
        pivoted: pd.DataFrame = data.pivot(
            index="period", columns="factor", values="ret"
        )
        return pivoted


class HistoricalDrawdownEstimatorTargetDataFormatter:
    @staticmethod
    def format(data: pd.DataFrame) -> pd.DataFrame:
        data.index = pd.to_datetime(data.index, unit="s")
        return data


class DrawdownCalculator:
    @staticmethod
    def calc(data: pd.DataFrame) -> pd.DataFrame:
        return data


class PrivateDrawdownPosition(TypedDict):
    start_idx: int
    end_idx: int
    dd_size: float


class Drawdown(TypedDict):
    start: str
    end: str
    mean: float
    stdev: float
    count: int


class HistoricalDrawdownEstimatorResult(TypedDict):
    regressions: RegressionResult
    drawdowns: List[Drawdown]


class HistoricalDrawdownEstimator:
    """
    Uses factor loadings to simulate hypothetical past performance
    of assets.

    Attributes
    ----------
    n : int
        The number of sims to run
    target_data : `pd.DataFrame`
        The asset whose performance we are trying to simulate
    factor_data : `pd.DataFrame`
        The factors used to simulate past performance
    merged_data : `pd.DataFrame`
        The formatted join of target_data and factor_data
    factors : `list[str]`
        List of factors in factor_data
    threshold : `float`
        Drawdown that will trigger recording
    reg_mod : `sm.OLS`
        StatsModels OLS regression model
    reg_res : `sm.regression.linear_model.RegressionResultsWrapper`
        Results of fitting OLS models
    sample_coefs : `ndarray`
        Use the results of the regression to build an estimate of historical factor loadings
    hypothetical_rets : `List[PrivateDrawdownPosition]`
        List of drawdown positions, used internally, not shown to client
    hypothetical_dd_dist : `Dict[Tuple[float], Tuple[float, float, int]]`
        Distribution of hypothetical drawdowns
    """

    def __init__(
        self,
        target_data: pd.DataFrame,
        factor_data: pd.DataFrame,
        factors: List[str],
        threshold: float,
        definition: RiskAttributionDefinition,
    ):
        self.n: int = 500
        self.target_data: pd.DataFrame = (
            HistoricalDrawdownEstimatorTargetDataFormatter.format(target_data)
        )
        self.factor_data: pd.DataFrame = (
            HistoricalDrawdownEstimatorFactorDataFormatter.format(factor_data)
        )
        self.factors: List[str] = factors
        self.threshold: float = threshold
        self.definition: RiskAttributionDefinition = definition

        self.build_data()
        self.build_regression()
        self.build_sample_coefs()
        self.estimator_algo()
        self.calc_drawdowns()
        self.group_drawdowns()
        return

    def get_results(self) -> HistoricalDrawdownEstimatorResult:
        return HistoricalDrawdownEstimatorResult(
            regressions=self.reg_result, drawdowns=self.drawdowns
        )

    def build_data(self) -> None:
        self.merged_data: pd.DataFrame = self.target_data.merge(
            self.factor_data,
            how="left",
            left_index=True,
            right_on="period",
        )
        self.merged_data.dropna(inplace=True)
        self.factor_rets: npt.NDArray[np.float64] = self.factor_data[
            self.factors
        ].values
        return

    def build_regression(self) -> None:
        x: pd.DataFrame = sm.add_constant(self.merged_data[self.factors])
        y: pd.DataFrame = self.merged_data[["daily_rt"]]
        self.reg_mod: sm.OLS = sm.OLS(y, x)
        self.reg_res: sm.regression.linear_model.RegressionResultsWrapper = (
            self.reg_mod.fit()
        )

        coefficients: List[RegressionCoefficient] = []
        ind_coefs: List[float] = self.reg_res.params.tolist()[1:]
        ind_errors: List[float] = self.reg_res.bse.tolist()[1:]

        for assetId, coef, error in zip(
            self.definition.ind,
            ind_coefs,
            ind_errors,
        ):
            coefficients.append(
                RegressionCoefficient(asset=assetId, coef=coef, error=error)
            )

        self.param_count = len(self.reg_res.params)
        self.reg_result = RegressionResult(
            intercept=self.reg_res.params[0], coefficients=coefficients
        )
        return

    def build_sample_coefs(self) -> None:
        self.sample_coefs: npt.NDArray[np.float64] = np.zeros(
            shape=(self.param_count, self.n), dtype=np.float64
        )
        for i, j, k in zip(
            self.reg_res.params, self.reg_res.bse, range(self.param_count)
        ):
            random_numbers: npt.NDArray[np.float64] = np.random.normal(i, j, self.n)
            self.sample_coefs[k] = random_numbers
        return

    def estimator_algo(self) -> None:
        stacked_coefs: npt.NDArray[np.float64] = self.sample_coefs.T
        self.hypothetical_rets: npt.NDArray[np.float64] = np.zeros(
            shape=(len(stacked_coefs), len(self.factor_rets)), dtype=np.float64
        )
        for i, j in zip(stacked_coefs, range(len(stacked_coefs))):
            sample_factor_weights: npt.NDArray[np.float64] = i[1:]
            sample_factor_rets: npt.NDArray[np.float64] = np.sum(
                sample_factor_weights * self.factor_rets, axis=1
            )
            self.hypothetical_rets[j] = sample_factor_rets
        return

    def calc_drawdowns(self) -> None:
        self.hypothetical_dd: List[PrivateDrawdownPosition] = []
        for i in self.hypothetical_rets:
            ##This is unesscessary, should really return a tuple
            dd_group: npt.NDArray[np.float64] = max_dd_threshold_position(
                i / 100,
                3,
                self.threshold,
            )
            if dd_group:
                for dd in dd_group:
                    dd_pos: PrivateDrawdownPosition = PrivateDrawdownPosition(
                        start_idx=int(dd[0]), end_idx=int(dd[1]), dd_size=dd[2]
                    )
                    self.hypothetical_dd.append(dd_pos)
        return

    def group_drawdowns(self) -> None:
        does_match: Callable[[Tuple[int, int], Tuple[int, int], int], bool] = (
            lambda dd, match, pos: match[pos] > dd[pos] - 5 and match[pos] < dd[pos] + 5
        )
        res: Dict[Tuple[int, int], List[float]] = {}
        for dd in self.hypothetical_dd:
            has_match: bool = False
            position: Tuple[int, int] = (dd["start_idx"], dd["end_idx"])
            for k in res:
                if does_match(k, position, 0):
                    has_match = True
                    res[k].append(dd["dd_size"])
            if not has_match:
                res[position] = [dd["dd_size"]]

        self.drawdowns: List[Drawdown] = []
        boundary: int = 0
        for i in res:
            if len(res[i]) > boundary:
                data_slice: pd.DataFrame = self.factor_data.iloc[i[0] : i[1]]
                start_date: str = str(data_slice.iloc[0].name)
                end_date: str = str(data_slice.iloc[-1].name)
                dd_data: npt.NDArray[np.float64] = np.array(res[i])
                drawdown = Drawdown(
                    start=start_date,
                    end=end_date,
                    mean=dd_data.mean(),
                    stdev=dd_data.std(),
                    count=len(dd_data),
                )
                self.drawdowns.append(drawdown)
        return


class HistoricalDrawdownEstimatorFromDataSources(HistoricalDrawdownEstimator):
    """
    Converts a dictionary of datasources into a HistoricalDrawdownEstimator.
    This supports one InvestPySource and N FactorSource objects. Throws
    an error when trying to estimate historical drawdown using non-factor
    sources.

    It is possible to use non-factor sources here but there isn't much
    reason to do since factors have a strong relationship with asset returns
    and other sources may not.
    """

    def __init__(
        self,
        dep: int,
        ind: List[int],
        model_prices: Dict[int, DataSource],
        threshold: float,
    ):
        """
        Parameters
        ----------
        model_prices: `dict[int, DataSource]`
            The assets we are trying to estimate drawdown for.
        threshold: `float`
            Drawdown that will trigger recording

        Throws
        ---------
        ValueError: when called with no FactorSource objects
        """
        definition: RiskAttributionDefinition = RiskAttributionDefinition(
            ind=ind, dep=dep, data=model_prices
        )

        flatten: Callable[[List[npt.NDArray[np.str0]]], List[Any]] = lambda t: [
            item for sublist in t for item in sublist
        ]
        factor_count: int = len(
            list(
                filter(
                    lambda x: type(x) == FactorSource,
                    definition.get_all(model_prices),
                )
            )
        )
        if factor_count != len(model_prices.values()) - 1:
            raise HistoricalDrawdownEstimatorNoFactorSourceException

        ind_prices: List[DataSource] = definition.get_ind_data(model_prices)
        dep_prices: DataSource = definition.get_dep_data(model_prices)

        if isinstance(dep_prices, FactorSource):
            ##FactorSource has to be independent variable
            raise HistoricalDrawdownEstimatorNoFactorSourceException

        factors: List[str] = flatten(
            [i.get_factors() for i in ind_prices if isinstance(i, FactorSource)]
        )
        factor_data: pd.DataFrame = pd.DataFrame({})
        if len(ind_prices) > 1:
            get_prices: Callable[[DataSource], pd.DataFrame] = lambda x: x.get_prices()
            factor_data = pd.concat(list(map(get_prices, ind_prices)))
        else:
            factor_data = ind_prices[0].get_prices()
        super().__init__(
            dep_prices.get_returns(), factor_data, factors, threshold, definition
        )
        return
