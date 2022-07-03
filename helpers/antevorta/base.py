from typing import TypedDict, List


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
    income_growth: float


class AntevortaResults(TypedDict):
    cash: float
    isa: float
    gia: float
    sipp: float
