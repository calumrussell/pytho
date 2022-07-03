from typing import List, Dict, TypedDict
import pandas as pd


class AlatorUnusableInputException(Exception):
    """Throws when BackTest has valid inputs but those inputs
    can't be used to create a valid BackTest
    """

    def __init__(self) -> None:
        self.message = "Data input cannot create a valid backtest"


class AlatorClientInput(TypedDict):
    assets: List[str]
    weights: List[float]


class AlatorPerformanceOutput(TypedDict):
    ret: float
    cagr: float
    vol: float
    mdd: float
    sharpe: float
    values: List[float]
    returns: List[float]
    dates: List[int]
