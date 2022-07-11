from typing import TypedDict, List


class AntevortaInsufficientDataException(Exception):
    """Throws when simulation has good inputs but there isn't enough
    data for the specified asset to create a simulation resampling from
    the data for that asset.

    Currently 365 days are required.
    """

    def __init__(self) -> None:
        self.message = "Asset has insufficient data to create an accurate simulation"


class AntevortaInvalidInputException(Exception):
    """Throws when BackTest is missing key inputs needed
    to complete
    """

    def __init__(self) -> None:
        self.message = "Missing either assets or weights or lengths are different"


class AntevortaUnusableInputException(Exception):
    """Throws when BackTest has valid inputs but those inputs
    can't be used to create a valid BackTest
    """

    def __init__(self) -> None:
        self.message = "Data input cannot create a valid backtest"


class AntevortaClientInput(TypedDict):
    assets: List[str]
    weights: List[float]
    initial_cash: float
    wage: float
    wage_growth: float
    contribution_pct: float
    emergency_cash_min: float
    sim_length: int


class AntevortaResults(TypedDict):
    cash: float
    isa: float
    gia: float
    sipp: float
