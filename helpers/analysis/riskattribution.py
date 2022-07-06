from turtle import window_width
import numpy as np
import numpy.typing as npt
import statsmodels.api as sm
from typing import Callable, Iterator, List, Dict, Optional, Tuple, TypedDict, Union
from arch.bootstrap import IIDBootstrap
from helpers.analysis.bootstrap import SemiParametricBootstrap

from helpers.prices.data import DataSource, FactorSource, InvestPySource, SourceFactory

DependentData = npt.NDArray[np.float64]
IndependentData = npt.NDArray[np.float64]
RegressionData = Tuple[DependentData, IndependentData]


class RegressionInput(TypedDict):
    ind: List[int]
    dep: int


class RollingRegressionInput(TypedDict):
    ind: List[int]
    dep: int
    window: int


class WindowLengthError(Exception):
    def __init__(self) -> None:
        super().__init__()
        self.message: str = "Window length longer than the data"


class RiskAttributionUnusableInputException(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message: str = message


class RegressionCoefficient(TypedDict):
    asset: int
    coef: float
    error: float


class RegressionResult(TypedDict):
    intercept: float
    coefficients: List[RegressionCoefficient]


class Average(TypedDict):
    asset: int
    avg: float


class RiskAttributionResult(TypedDict):
    regression: RegressionResult
    avgs: List[Average]
    min_date: int
    max_date: int


class RiskAttributionDefinition:
    """
    Wraps around the data, controls how clients call for data from the
    DataSource, also used to error check both the inputs and the DataSources.
    """

    @staticmethod
    def _formatter() -> Callable[[List[IndependentData]], IndependentData]:
        return lambda d: np.array(list(map(lambda x: list(x), zip(*d))))

    @staticmethod
    def _to_daily_rt(
        dates: List[int],
    ) -> Callable[[Union[FactorSource, InvestPySource]], npt.NDArray[np.float64]]:
        return lambda x: SourceFactory.find_dates(
            dates, x, x.__class__
        ).get_returns_list()

    def _get_dep_source(self) -> DataSource:
        dep: Union[DataSource, None] = self.data.get(self.dep)
        if not dep:
            raise RiskAttributionUnusableInputException(
                "Dependent variable data not found"
            )
        else:
            return dep

    def _get_ind_source(self) -> List[DataSource]:
        res: List[DataSource] = []
        for i in self.data:
            ind_source: Union[DataSource, None] = self.data.get(i)
            if not ind_source:
                raise RiskAttributionUnusableInputException(
                    "Missing Independent variable"
                )
            else:
                res.append(ind_source)
        return res

    def get_all_sources(self) -> List[DataSource]:
        return [self._get_dep_source(), *self._get_ind_source()]

    def _get_dates_union(self) -> List[int]:
        date_lists = [set(i.get_dates()) for i in self.get_all_sources()]
        union_of_dates = set.intersection(*date_lists)
        return sorted([int(i) for i in union_of_dates])

    def get_dates_union(self) -> List[int]:
        return self.dates_union

    def get_ind_data(self, dates: Optional[List[int]] = None) -> IndependentData:
        res: npt.NDArray[np.float64] = np.array([])
        for i in self.ind:
            ind_data: Union[DataSource, None] = self.data.get(i)
            if ind_data:
                if not dates:
                    dates = self.dates_union
                data: npt.NDArray[np.float64] = RiskAttributionDefinition._to_daily_rt(
                    dates
                )(ind_data)
                res = np.append(res, data)
        return res.reshape(len(dates), len(self.ind))

    def get_dep_data(self, dates: Optional[List[int]] = None) -> DependentData:
        val: Union[DataSource, None] = self.data.get(self.dep)
        if not val:
            raise RiskAttributionUnusableInputException(
                "Dependent variable data not found"
            )
        else:
            if not dates:
                dates = self.dates_union
            data: npt.NDArray[np.float64] = RiskAttributionDefinition._to_daily_rt(
                dates
            )(val)
            return data

    def __init__(self, reg_input: RegressionInput, data: Dict[int, DataSource]):
        self.ind: List[int] = [int(i) for i in reg_input["ind"]]
        self.dep: int = int(reg_input["dep"])
        self.data: Dict[int, DataSource] = data
        self.dates_union: List[int] = self._get_dates_union()

        if not reg_input["dep"] in data:
            raise RiskAttributionUnusableInputException(
                "Missing dependendent variable data"
            )

        if not set(reg_input["ind"]).issubset(data):
            raise RiskAttributionUnusableInputException(
                "Missing independent variable data"
            )

        if not self.dates_union:
            raise RiskAttributionUnusableInputException(
                "No overlapping dates in data, cannot run analysis with inputs"
            )
        return


class RiskAttributionBase:
    """RiskAttributionBase defines common functions for
    any RiskAttribution model.

    Attributes
    ----------
    defintion: `RiskAttributionDefinition`
        Defines dependent and independent variables
    data: `Dict[int,DataSource]`
        Integer-indexed dictionary of objects conforming to the DataSource
        interface.
    dates: `List[int]`
        The union of dates between all the datasets
    """

    def get_windows(self, window_length: int) -> Iterator[RegressionData]:
        dates: List[int] = self.definition.get_dates_union()
        dep_data: DataSource = self.definition.get_dep_data()
        dep_length: int = len(dep_data)

        if dep_length < window_length:
            raise WindowLengthError

        windows: range = range(window_length, len(dates))
        for w in windows:
            window_dates: List[int] = dates[w - window_length : w]

            dep: DependentData = self.definition.get_dep_data(window_dates)
            ind: IndependentData = self.definition.get_ind_data(window_dates)
            yield dep, ind

    def get_data(self) -> RegressionData:
        """
        NOTE:The original format is (number of days, number of assets)
        and we need to transpose to (number of assets, number of
        days) for regression
        """
        ##This function should either run on a slice of the data
        ##which can be passed into the function
        ##or should default to just fetching all the data at once
        dep_data: DependentData = self.definition.get_dep_data()
        ind_data: IndependentData = self.definition.get_ind_data()
        return dep_data, ind_data

    def _run_regression(
        self, ind: IndependentData, dep: DependentData
    ) -> RegressionResult:
        reg_mod: sm.OLS = sm.OLS(dep, sm.add_constant(ind))
        reg_res: sm.regression.linear_model.RegressionResultsWrapper = reg_mod.fit()

        coefs = []
        for i, j, k in zip(
            self.definition.ind,
            reg_res.params.tolist()[1:],
            reg_res.params.tolist()[1:],
        ):
            ##Error can be infinity which is non-JSON, casting output to string
            error = k
            if k == np.inf:
                error = -1
            coefs.append(RegressionCoefficient(asset=int(i), coef=j, error=error))
        return RegressionResult(
            intercept=reg_res.params.tolist()[0], coefficients=coefs
        )

    def _build_data(self) -> None:
        raise NotImplementedError()

    def __init__(
        self, definition: RiskAttributionDefinition, data: Dict[int, DataSource]
    ):
        self.definition: RiskAttributionDefinition = definition
        self.data: Dict[int, DataSource] = data


class RiskAttribution(RiskAttributionBase):
    """RiskAttribution model that uses all the data for the assets
    to estimate the composition of the dependent asset's risk.

    Attributes
    ---------
    ind_data: `IndependentData npt.NDArray[np.float64]`
        Formatted independent data
    dep_data: `DepedendentData npt.NDArray[np.float64]`
        Formatted dependent data
    """

    def _build_data(self) -> None:
        self.dep_data, self.ind_data = self.get_data()

    def run(self) -> RiskAttributionResult:
        avgs = [
            Average(asset=int(i), avg=(sum(j) / len(j)))
            for i, j in zip(self.definition.ind, np.array(self.ind_data).T)
        ]
        avgs.append(
            Average(
                asset=int(self.definition.dep),
                avg=(sum(self.dep_data) / len(self.dep_data)),
            )
        )
        dates: List[int] = self.definition.get_dates_union()
        return RiskAttributionResult(
            regression=self._run_regression(self.ind_data, self.dep_data),
            avgs=avgs,
            min_date=min(dates),
            max_date=max(dates),
        )

    def __init__(self, reg_input: RegressionInput, data: Dict[int, DataSource]):
        definition: RiskAttributionDefinition = RiskAttributionDefinition(
            reg_input, data
        )
        super().__init__(definition, data)
        self._build_data()


class RollingRiskAttributionResult(TypedDict):
    regressions: List[RegressionResult]
    min_date: int
    max_date: int
    dates: List[int]
    averages: List[List[Average]]


class RollingRiskAttribution(RiskAttributionBase):
    """RiskAttribution model that calculated the composition
    of the dependent asset's risk over rolling periods of N
    length.

    Attributes
    --------
    window_length : int
        Length of the rolling windows over which the analysis will run
    """

    def run(self) -> RollingRiskAttributionResult:
        regressions: List[RegressionResult] = []
        avgs: List[List[Average]] = []
        for dep, ind in self.get_windows(self.window_length):
            avg_group = [
                Average(asset=int(i), avg=(sum(j) / len(j)))
                for i, j in zip(self.definition.ind, np.array(ind).T)
            ]
            avg_group.append(
                Average(
                    asset=int(self.definition.dep),
                    avg=(sum(dep) / len(dep)),
                )
            )
            avgs.append(avg_group)
            regressions.append(self._run_regression(ind, dep))
        # Rolling window won't have the first N dates
        dates: List[int] = self.definition.get_dates_union()
        clipped_dates: List[int] = dates[self.window_length :]
        return RollingRiskAttributionResult(
            regressions=regressions,
            averages=avgs,
            min_date=min(clipped_dates),
            max_date=max(clipped_dates),
            dates=clipped_dates,
        )

    def __init__(
        self,
        roll_input: RollingRegressionInput,
        data: Dict[int, DataSource],
    ):

        reg_input = RegressionInput(ind=roll_input["ind"], dep=roll_input["dep"])
        definition: RiskAttributionDefinition = RiskAttributionDefinition(
            reg_input, data
        )
        super().__init__(definition, data)
        self.window_length: int = roll_input["window"]


class BootstrapResult(TypedDict):
    asset: int
    lower: float
    upper: float


class BootstrapRiskAttributionResult(TypedDict):
    intercept: BootstrapResult
    coefficients: List[BootstrapResult]


class BootstrapRiskAttributionAlt:
    """
    RiskAttribution model that constructs bootstrap estimates
    of the dependent asset's risk using own semi-parametric
    bootstrap

    Attributes
    --------
    window_length : int
        Length of the rolling windows over which the analysis will run
    """

    def run(self) -> BootstrapRiskAttributionResult:
        dep_data: DependentData = self.definition.get_dep_data()
        ind_data: IndependentData = self.definition.get_ind_data()
        bs = SemiParametricBootstrap.run(dep_data, ind_data)

        intercept_result = BootstrapResult(
            asset=int(self.definition.dep),
            lower=bs.confidence_interval.low[0],
            upper=bs.confidence_interval.high[0],
        )
        coefs_result: List[BootstrapResult] = [
            BootstrapResult(
                asset=int(self.definition.ind[i]),
                lower=bs.confidence_interval.low[i + 1],
                upper=bs.confidence_interval.high[i + 1],
            )
            for i in range(len(self.definition.ind))
        ]
        return BootstrapRiskAttributionResult(
            intercept=intercept_result, coefficients=coefs_result
        )

    def __init__(self, reg_input: RegressionInput, data: Dict[int, DataSource]):
        self.definition: RiskAttributionDefinition = RiskAttributionDefinition(
            reg_input, data
        )


class BootstrapRiskAttribution(RiskAttributionBase):
    """RiskAttribution model that constructs a bootstrap estimates
    of the dependent asset's risk using the result of the
    RollingRiskAttribution run

    Attributes
    --------
    window_length : int
        Length of the rolling windows over which the analysis will run
    """

    def _get_coefs_from_rolling_results(
        self, rolling: RollingRiskAttributionResult
    ) -> npt.NDArray[np.float64]:
        coefs: List[List[float]] = []
        for reg in rolling["regressions"]:
            temp: List[float] = []
            for coef in reg["coefficients"]:
                temp.append(coef["coef"])
            coefs.append(temp)
        return np.array(coefs).T

    def _get_avgs_from_rolling_results(
        self, rolling: RollingRiskAttributionResult
    ) -> npt.NDArray[np.float64]:
        avgs: List[List[float]] = []
        for avg_group in rolling["averages"]:
            temp: List[float] = []
            for avg in avg_group:
                temp.append(avg["avg"])
            avgs.append(temp)
        return np.array(avgs).T

    def _build_bootstrap(
        self, rolling: RollingRiskAttributionResult
    ) -> BootstrapRiskAttributionResult:
        """Each data point is a list of lists. We can have one intercept but need to put
        that into a list so we can merge it later. We can have multiple coefs and avgs
        so these naturally go into a list of lists. Each row is one coefficient or one average,
        and the columns are the length of the dataset.
        We then concat and transpose so each col is of length # of coefs + # of avgs + 1 (for intercept),
        and the number of rows is the length of the dataset.
        We then put this into bootstrap which calculates the mean for each column, and then uses
        this to construct bootstrap estimates. The length of the estimates is equal to
        # of coefs + # of avgs + 1 (for intercept). We transpose the results so we get conf intervals
        for each variable.
        """
        intercepts: npt.NDArray[np.float64] = np.array(
            [[i["intercept"] for i in rolling["regressions"]]]
        )
        coefs: npt.NDArray[np.float64] = self._get_coefs_from_rolling_results(rolling)
        avgs: npt.NDArray[np.float64] = self._get_avgs_from_rolling_results(rolling)
        merged: npt.NDArray[np.float64] = np.concatenate((intercepts, coefs, avgs), axis=0).T  # type: ignore
        bootstrap: IIDBootstrap = IIDBootstrap(merged)
        bootstrap_results: npt.NDArray[np.float64] = bootstrap.conf_int(
            lambda x: x.mean(axis=0), method="basic"
        ).T
        ind_variable_cnt: int = len(self.definition.ind)
        ##This line removes the bootstrap estimates for the averages, calculated so we can potentially
        ##add back in later

        intercept_result = BootstrapResult(
            asset=int(self.definition.dep),
            lower=bootstrap_results[0][0],
            upper=bootstrap_results[0][1],
        )

        coefs_result: List[BootstrapResult] = [
            BootstrapResult(
                asset=int(self.definition.ind[pos]), lower=res[0], upper=res[1]
            )
            for pos, res in enumerate(bootstrap_results[1 : 1 + ind_variable_cnt])
        ]
        return BootstrapRiskAttributionResult(
            intercept=intercept_result, coefficients=coefs_result
        )

    def run(self) -> BootstrapRiskAttributionResult:
        rra: RollingRiskAttribution = RollingRiskAttribution(
            roll_input=RollingRegressionInput(
                ind=self.definition.ind,
                dep=self.definition.dep,
                window=self.window_length,
            ),
            data=self.data,
        )
        rolling_results: RollingRiskAttributionResult = rra.run()
        return self._build_bootstrap(rolling_results)

    def __init__(self, roll_input: RollingRegressionInput, data: Dict[int, DataSource]):
        reg_input = RegressionInput(ind=roll_input["ind"], dep=roll_input["dep"])
        definition: RiskAttributionDefinition = RiskAttributionDefinition(
            reg_input, data
        )
        super().__init__(definition, data)
        self.window_length: int = roll_input["window"]
