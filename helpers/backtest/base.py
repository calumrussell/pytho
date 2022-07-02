from typing import List, Dict, TypedDict
import pandas as pd


class BackTestInvalidInputException(Exception):
    """Throws when BackTest is missing key inputs needed
    to complete
    """

    def __init__(self) -> None:
        self.message = "Missing either assets or weights or lengths are different"


class BackTestUnusableInputException(Exception):
    """Throws when BackTest has valid inputs but those inputs
    can't be used to create a valid BackTest
    """

    def __init__(self) -> None:
        self.message = "Data input cannot create a valid backtest"


class BackTestResults(TypedDict):
    ret: float
    cagr: float
    vol: float
    mdd: float
    sharpe: float
    values: List[float]
    returns: List[float]
    dates: List[int]
