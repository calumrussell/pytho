from panacea import AntevortaBasicInput, antevorta_basic, InsufficientDataError  # type: ignore

from api.models import Coverage
from helpers import prices

from .base import (
    AntevortaClientInput,
    AntevortaResults,
    AntevortaUnusableInputException,
    AntevortaInsufficientDataException,
)


class DefaultSimulationWithPriceAPI:
    """Initialises and loads the data to be used by the simulation.

    Doesn't test for malformed input as all of the input tests are carried out in
    the API front end

    Attributes
    ---------
    weights: `List[float]`
    coverage: `List[Coverage]`
    signal: `Dict[str, float]`
    initial_cash: float
    wage: float
    wage_growth: float
    contribution_pct: float
    emergency_cash_min: float
    sim_length: int
    results: `AntevortaResults`

    Raises
    ---------
    AntevortaUnusableInputException
        Input is valid but there is no data source
    AntevortaInsufficientDataException
        Input is valid but we don't have sufficient data to create simulation
    ConnectionError
        Failed to connect to InvestPySource
    """

    def run(self) -> None:
        price_request = prices.PriceAPIRequests(self.coverage)
        try:
            inc_sources = price_request.get_overlapping()
        except Exception:
            raise AntevortaUnusableInputException

        dates = None
        close = {}
        for source in inc_sources:
            if dates is None:
                dates = list(inc_sources[source].get_dates())
            close[str(source)] = inc_sources[source].get_close()["Close"].to_list()

        if not close or not dates:
            raise AntevortaUnusableInputException

        coverage_ids = [str(c.id) for c in self.coverage]
        inc_in = AntevortaBasicInput(
            assets=coverage_ids,
            dates=dates,
            weights=self.signal,
            close=close,
            initial_cash=self.initial_cash,
            wage=self.wage,
            wage_growth=self.wage_growth,
            contribution_pct=self.contribution_pct,
            emergency_cash_min=self.emergency_cash_min,
            sim_length=self.sim_length,
        )

        try:
            inc = antevorta_basic(inc_in)

            self.results = AntevortaResults(
                cash=inc[0],
                isa=inc[1],
                gia=inc[2],
                sipp=inc[3],
            )
        except InsufficientDataError:
            raise AntevortaInsufficientDataException
        return

    def __init__(self, antevorta: AntevortaClientInput):
        self.weights = antevorta["weights"]
        try:
            self.coverage = Coverage.objects.filter(id__in=antevorta["assets"])
        except ValueError:
            raise AntevortaUnusableInputException

        if not self.coverage:
            raise AntevortaUnusableInputException

        if len(self.coverage) != len(antevorta["assets"]):
            raise AntevortaUnusableInputException

        self.signal = {str(i): j for (i, j) in zip(antevorta["assets"], self.weights)}
        self.initial_cash = antevorta["initial_cash"]
        self.wage = antevorta["wage"]
        self.wage_growth = antevorta["wage_growth"]
        self.contribution_pct = antevorta["contribution_pct"]
        self.emergency_cash_min = antevorta["emergency_cash_min"]
        self.sim_length = antevorta["sim_length"]
        return
